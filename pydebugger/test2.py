import inspect
import debug

class parent(object):
	def __init__(self):
		super(parent, self)

	def test_a(self):
		#debug.debug('cls')
		print "TEST A"
		print "inspect.stack A =", inspect.stack()#[0][1]
		print "-"*50
		debug.debug(cls='cls')
		defname = str(inspect.stack()[1][3])
		print "defname =", defname
		debug.debug(defname_x=defname)		
		for i in inspect.stack():
			print i
			print type(i)
			print i[2], type(i[2])
			print "+"*50
		
	def test_b(self):
		print "TEST B"
		print "inspect.stack B =", inspect.stack()#[0][1]
		self.test_a()
		
	def test_c(self):
		print "TEST C"
		print "inspect.stack C =", inspect.stack()#[0][1]
		self.test_b()
		
	def test(self):
		pass
def test():
	print "inspect.stack =", inspect.stack()[0][1]
	
	
c  = parent()
c.test_c()
