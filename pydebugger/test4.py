from __future__ import print_function
from make_colors import make_colors
linenumbers = "[10]"
PID = "1029304"
linenumbers = " " + make_colors(str(linenumbers), 'red', 'on_white') + "] " + make_colors("PID:", 'red', 'lightgreen') + make_colors(str(PID), 'lightwhite')
print("linenumbers =", linenumbers)
