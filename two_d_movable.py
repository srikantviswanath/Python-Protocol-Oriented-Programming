'''
Use case depicting the power of Contract @borrow functions that provide a place for
implementing common functionality
'''
from contracts_core import Contract, required, borrow

class TwoDMovable(object):

	@required
	def relativeMoveBy(self, x, y): pass

	@borrow()
	def moveHorizontally(self, lateralMove):
		'''
		powerful abstraction happening here. moveHorizontally does not care what the underlying
		implementation of relativeMoveBy() is. As we see below Circle class has different implementation 
		as Point class
		'''
		self.relativeMoveBy(lateralMove, 0)

@Contract(TwoDMovable)
class Point(object):

	def __init__(self, x, y):
		self.x = x
		self.y = y

	def relativeMoveBy(self, x, y):
		self.x += x
		self.y += y

@Contract(TwoDMovable)
class Circle(object):

	def __init__(self, centerX, centerY, radius):
		self.centerX = centerX
		self.centerY = centerY
		self.radius = radius

	def relativeMoveBy(self, x, y):
		self.centerX += 2+x
		self.centerY += 2+y

if __name__ == '__main__':
	p = Point(3,4)
	p.moveHorizontally(3) 
	print p.x, p.y #Point at (6, 4)

	c = Circle(10, 15, 5)
	c.moveHorizontally(5) 
	print c.centerX, c.centerY #Center at (17,17)