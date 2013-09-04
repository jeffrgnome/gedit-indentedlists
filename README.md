gedit-indentedlists
===================

Indented markdown or text lists in GEdit.

This is a plugin for GEdit v3.x. It isn't as stable as I would like it to be, but it makes editing markdown in GEdit less painful. I like to use this tool in conjunction with the Chrome Plugin called "Markdown Viewer" so I can preview the markdown in nearly realtime.

Features implemented:
* Pressing tab or shift+tab to indent and unindent lists
	* This works regardless of where the cursor is in the line
* Shift+Enter breaks out of a list

1) Numbered lists work fairly well
2) It increments the number for you.
	3) But when you indent, the tool isn't currently smart enough to start with a letter 'a' or otherwise.
4) Going back keeps on numbering. :(

1) Still, pretty useful for non-indented numbered lists.
2) The numbering works fine for that scenario.
3) Give it a try!

89) Can start on any number desired.
90) And it will count up from there.

Features I hope to implement soon:
* I want backspace on an indented list to either unindent or remove the " *" (or " +" " -" etc).
* Fix the numbering issue mentioned above.
* Pressing tab on a line with a number (such as "10") has the unintended consequence of indenting **before** the number, rather than **after**. But that's a pretty rare thing. I'll fix that some day.
* Undefined behavior when you use spaces instead of tabs in your GEdit preferences. I didn't have time to test that.
* For some reason, the plugin doesn't seem to engage until you save the file. So writing in an untitled document doesn't work. Save it to fix this. (This may just be a GEdit known issue or bug..)

Feel free to contribute and make it more stable. I just wrote the bare minimum to get me by for making markdown my preferred way to take lecture notes in school!
