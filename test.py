# from debug import *
from debug2 import debug as debug2
from debug import debug
import os
os.environ.update({'DEBUG':'1'})
os.environ.update({'DEBUG_SERVER':'1'})
# import sys
# import traceback
debug(print_debug="TEST STRING ERROR")
debug2(print_debug2="TEST STRING ERROR")

def function_test(param1, param2, param3):
	debug(print_function_parameters=True)

function_test("test_parameter_1", "test_parameter_2", "test_parameter_3")

import test2
test2.test()
