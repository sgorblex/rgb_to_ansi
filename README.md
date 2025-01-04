# RGB to ANSI
Simple script that converts RGB escape codes (truecolor) for terminal emulators to 16-color ANSI escape codes.

Because you're going from 16 million colors to 16 colors (lol), the reference palette will most likely need a per-input adjustment.
The script contains an option to use a custom palette, while the default one is close to the RGB values of the 16 colors of the tty on my machine.
To produce a pleasing palette, a good method is to set e.g. "green" to an RGB value close to what you would like to be green in the output.
Use the given alternate palette as a reference for the json format.
Remember to test the 16 colors on your tty as they can be quite different from what your graphical terminal emulator displays ("yellow" is actually orange).


## License
[GPL v.3](https://www.gnu.org/licenses/gpl-3.0.en.html)
