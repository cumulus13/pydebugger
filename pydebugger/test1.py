#from debug import *
#import sys
#import traceback

#def function_test(param1, param2, param3):
	#debug(print_function_parameters=True)

#function_test("test_parameter_1", "test_parameter_2", "test_parameter_3")

from debug import *

def test1():
	return "test1"

def test2():
	return "test2"

def test3():
	return "test3"

data1 = test1()
data2 = test2()
data3 = test3()

debug(data1, data2, data3, "data4")

print("#" *120)

import inspect

class Test:

	@classmethod
	def printlist(cls, *args, **kwargs):
		
		print("args [3] =", args)
		
		caller_locals = inspect.currentframe().f_back.f_locals

		printed = False

		for arg in args:
			if isinstance(arg, str):
				found = False
				for name, value in caller_locals.items():
					if arg == name or (callable(value) and hasattr(value, '__name__') and value.__name__ == arg):
						found = True
						print(f"{name} = {value.__name__}")
						printed = True
						break
				if not found:
					printed = True
					print(f"start {arg} ..........")
			else:
				variables = [name for name, value in caller_locals.items() if value == arg]
				if variables:
					printed = True
					for name in variables:
						print(f"{name} = {arg}")

		if not printed:
			print("No matching variables or functions found.")

	#@classmethod
	#def test1(cls):
		#return "test1"

	#@classmethod
	#def test2(cls):
		#return "test2"

	#@classmethod
	#def test3(cls):
		#return "test3"

#data1 = Test.test1()
#data2 = Test.test2()
#data3 = Test.test3()

Test.printlist(data1, data2, data3, 'data4')
