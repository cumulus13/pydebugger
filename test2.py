import inspect

def test():
	print "inspect.stack =", inspect.stack()[0][1]