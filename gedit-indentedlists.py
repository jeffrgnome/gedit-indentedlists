#  gedit-indentedlists.py
#
#  Copyright (C) 2013 - Jeff Reed
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor,
#  Boston, MA 02110-1301, USA.

from gi.repository import GObject, Gtk, Gdk, GtkSource, Gedit

class IndentedListsPlugin(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "IndentedListsPlugin"

    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)
     
    def do_activate(self):
        self._handlers = [
            None,
            self.view.connect('notify::editable', self.on_notify),
            self.view.connect('notify::insert-spaces-instead-of-tabs', self.on_notify)
        ]

    def do_deactivate(self):
        for handler in self._handlers:
            if handler is not None:
                self.view.disconnect(handler)

    def update_active(self):
        # Don't activate the feature if the buffer isn't editable or if
        # we're using spaces
        active = self.view.get_editable() and \
                 not(self.view.get_insert_spaces_instead_of_tabs())

        if active and self._handlers[0] is None:
            self._handlers[0] = self.view.connect('key-press-event',
                                                   self.on_key_press_event)
        elif not active and self._handlers[0] is not None:
            self.view.disconnect(self._handlers[0])
            self._handlers[0] = None

    def on_notify(self, view, pspec):
        self.update_active()

    def on_key_press_event(self, view, event):
        #Bail out if text is selected
        doc = view.get_buffer()
        if doc.get_has_selection():
            return False

        # If we're at the begining of the line,
        # then, we don't have a need for anything special
        cur = doc.get_iter_at_mark(doc.get_insert())
        offset = cur.get_line_offset()
        if offset == 0:
            return False

	#Collect some state helpers
        mods = Gtk.accelerator_get_default_mod_mask()
        shift_pressed = event.state & Gdk.ModifierType.SHIFT_MASK != 0

        if event.keyval == Gdk.KEY_Return and event.state & mods == 0:
            return self.HandleReturn(doc, cur)

        if event.keyval == Gdk.KEY_Tab and not(shift_pressed):
            return self.HandleTab(doc, cur)

        if shift_pressed and event.keyval == Gdk.KEY_ISO_Left_Tab:
            return self.HandleShiftTab(doc, cur)

#        if event.keyval == Gdk.KEY_BackSpace:
#            return self.HandleBackSpace(doc, cur)

        return False # We didn't handle this event, pass it on

    def HandleReturn(self, doc, cur):

        line_number = cur.get_line()
        begin = doc.get_iter_at_line_offset(line_number, 0)
        new_line_prepend = ['\n']
        should_process = False
        last_char = None

        while begin.compare(cur) == -1:
            begin_char = begin.get_char()
            if (begin_char == '+' or begin_char == '*' or begin_char == '-' or begin_char == '0' or begin_char == '1' or begin_char == '2' or begin_char == '3' or begin_char == '4' or begin_char == '5' or begin_char == '6' or begin_char == '7' or begin_char == '8' or begin_char == '9'):
                should_process = True
                last_char = begin_char
                break
            elif not(begin_char == '	' or begin_char == ' '): # TAB or SPACE
                should_process = False
                break
            else:
                new_line_prepend.append(begin_char)
                begin.forward_char()

        #If we already know this isn't a "special" list return, bail out
        if should_process == False:
            return False

        if (last_char == '0' or last_char == '1' or last_char == '2' or last_char == '3' or last_char == '4' or last_char == '5' or last_char == '6' or last_char == '7' or last_char == '8' or last_char == '9'):
            # Might be continuing a numbered list. Look for ")"
            should_process = False
            number_buffer = [last_char]
            begin.forward_char()
            while begin.compare(cur) == -1:
                begin_char = begin.get_char()
                if (begin_char == '0' or begin_char == '1' or begin_char == '2' or begin_char == '3' or begin_char == '4' or begin_char == '5' or begin_char == '6' or begin_char == '7' or begin_char == '8' or begin_char == '9'):
                    number_buffer.append(begin_char)
                    begin.forward_char()
                elif begin_char == ')' or begin_char == '.' or begin_char == ':':
                    int_number = int(''.join(number_buffer))
                    int_number = int_number + 1
                    new_line_prepend.append(int_number.__str__())
                    new_line_prepend.append(begin_char)
                    should_process = True
                    break
                else:
                    break

            #If this was just a number preceded by tabs/spaces,
            # or we ran into unexpected chars, or ran out of characters, bail out
            if should_process == False:
                return False
        else:
            #Check next char, and if same, bail
            if begin.compare(cur) == -1:
                begin_char = begin.get_char()
                look_ahead = begin.copy()
                look_ahead.forward_char()
                la_char = look_ahead.get_char()
                if begin_char == la_char:
                    # This is not a list. It's probably a horizontal line. Bail out.
                    return False
            new_line_prepend.append(last_char) # prepend a '*' or '-'

        # Insert a new line, continuing the existing list
        if(len(new_line_prepend) > 0):
            new_line_prepend.append(' ')
            doc.begin_user_action()
            insert_this = ''.join(new_line_prepend)
            doc.insert_interactive(cur, insert_this, len(insert_this), self.view.get_editable())
            doc.end_user_action()

            # This didn't help. I'm not sure how to scroll when you enter off-screen...
            # self.view.scroll_to_iter(cur, 0.5, False, 0, 0)

            return True
        else:
            return False

    def HandleTab(self, doc, cur):

        line_number = cur.get_line()
        begin = doc.get_iter_at_line_offset(line_number, 0)
        insert_tab_here = None

        while begin.compare(cur) == -1 and insert_tab_here is None:
            begin_char = begin.get_char()
            if (begin_char == '+' or begin_char == '*' or begin_char == '-' or begin_char == '0' or begin_char == '1' or begin_char == '2' or begin_char == '3' or begin_char == '4' or begin_char == '5' or begin_char == '6' or begin_char == '7' or begin_char == '8' or begin_char == '9'):
                insert_tab_here = begin.copy()
            elif not(begin_char == '	' or begin_char == ' '): # TAB or SPACE
                break
            else:
                begin.forward_char()

        if insert_tab_here is None:
            # Nothing found to do. Bail out.
            return False
        else:
            if begin.compare(cur) == -1:
                begin.forward_char()
                begin_char = begin.get_char()
                if begin_char == '+' or begin_char == '-' or begin_char == '*':
                    # This is not a list. It's probably a horizontal line. Bail out.
                    return False

            # Insert a tab before the list item
            doc.begin_user_action()
            doc.insert_interactive(insert_tab_here, '	', 1, self.view.get_editable())
            doc.end_user_action()
            return True

    def HandleShiftTab(self, doc, cur):

        line_number = cur.get_line()
        begin = doc.get_iter_at_line_offset(line_number, 0)
        remove_tab_here = None

        while begin.compare(cur) == -1 and remove_tab_here is None:
            begin_char = begin.get_char()
            if (begin_char == '+' or begin_char == '*' or begin_char == '-' or begin_char == '0' or begin_char == '1' or begin_char == '2' or begin_char == '3' or begin_char == '4' or begin_char == '5' or begin_char == '6' or begin_char == '7' or begin_char == '8' or begin_char == '9'):
                remove_tab_here = begin
            elif not(begin_char == '	' or begin_char == ' '): # TAB or SPACE
                break
            else:
                begin.forward_char()

        if remove_tab_here is None:
            # Nothing found to do. Bail out.
            return False
        else:
            if remove_tab_here.get_line_offset() > 0:
                # There is a tab to remove. Remove it.
                remove_end = remove_tab_here.copy()
                remove_tab_here.backward_char()
                doc.begin_user_action()
                doc.delete(remove_tab_here, remove_end)
                doc.end_user_action()
                return True
            else:
                # Bail out
                return False

    #TODO: Pretty buggy
    # If you have " - my stuff, and oops", and you hit backspace, you lose the whole line
    #    Need to detect when you're at the beginning of a list item, and only apply backspace then
    def HandleBackSpace(self, doc, cur):

        line_number = cur.get_line()
        begin = doc.get_iter_at_line_offset(line_number, 0)
        is_list_item = None

        while begin.compare(cur) == -1 and is_list_item is None:
            begin_char = begin.get_char()
            if (begin_char == '+' or begin_char == '*' or begin_char == '-'):
                is_list_item = begin
            elif not(begin_char == '	' or begin_char == ' '): # TAB or SPACE
                break
            else: # if it's a tab or space
                begin.forward_char()

        if is_list_item is None:
            # Nothing found to do. Bail out.
            return False
        else:
            if begin.compare(cur) == -1:
                begin.forward_char()
                begin_char = begin.get_char()
                if begin_char == '+' or begin_char == '-' or begin_char == '*':
                    # This is not a list. It's probably a horizontal line. Bail out.
                    return False
                
            # Clear the curent line
            begin = doc.get_iter_at_line_offset(line_number, 0)
            doc.begin_user_action()
            doc.delete(begin, cur)
            doc.end_user_action()
            return True
