import inspect

class parent(object):
	def __init__(self):
		super(parent, self)

	def test_a(self):
		print "TEST A"
		print "inspect.stack A =", inspect.stack()#[0][1]
		
	def test_b(self):
		print "TEST B"
		print "inspect.stack B =", inspect.stack()#[0][1]
                self.test_a()
		
	def test_c(self):
		print "TEST C"
		print "inspect.stack C =", inspect.stack()#[0][1]
                self.test_b()

c = parent()
c.test_c()

def test():
	print "inspect.stack =", inspect.stack()[0][1]
