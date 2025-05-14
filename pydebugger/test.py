import os
os.environ.update({'DEBUG_SERVER':'1'})
from debug import debug, debug2, debug3, debug4

debug(TEST_debug = "TEST", debug = 1)
debug2(TEST_debug = "TEST2")
debug3(TEST_debug = "TEST3")
debug4(TEST_debug = "TEST4")