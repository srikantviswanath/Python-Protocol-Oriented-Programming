'''
An example to depict the types-dependecy inference of protocol extensions.
Inspired by http://sam.dods.co/blog/2015/08/04/why-i-love-swift-protocol-extensions/
Thanks to Sam Dods
'''
from contracts_core import Contract, required, borrow

class MediaItem(object):

	copyRightsAgreement = 'Yet another lisencing agreement...'


class Compressible(object):

	__reqdattribs__ = dict(compressFactor=float)

	@required
	def compress(*args): pass

class Sharable(object):

	__reqdattribs__ = dict(name=str)

	@borrow()
	def share(self, *args):
		print 'Sharing {filename}'.format(filename=self.name)

	@borrow(MediaItem)
	def share(self, *args):
		print 'Hoping you read thru the following lisence agreement:'
		print self.copyRightsAgreement
		print 'Sharing...'

	@borrow(MediaItem, Compressible)
	def share(self, *args):
		print 'Generating liscence agreement:' + '.' * 10
		print self.copyRightsAgreement
		print '*' * 20
		print 'Preparing to compress ...'
		self.compress()
		print 'Sharing' + '.' * 15

@Contract(Sharable)
class UserProfile(object):

	def __init__(self, profilename):
		self.name = profilename

@Contract(Sharable)
class AudioClip(MediaItem):

	def __init__(self, filename):
		self.name = filename

@Contract(Sharable, Compressible)
class Image(MediaItem):
	
	def __init__(self, filename):
		self.name = filename
		self.compressFactor = 1.6

	def compress(self):
		print 'Compressing {img} by {factor}'.format(img=self.name, factor=self.compressFactor)


class Movie(MediaItem):
	
	def __init__(self, filename):
		self.name = filename

if __name__ == '__main__':
	'''ac = AudioClip('coldplay_01.wav')
	ac.share() # >>'Hoping you read thru the following lisence agreement:'''

	img = Image('picaso_01.jpg')
	img.share() # >> 'Hoping you read thru the following lisence agreement:'

	#up = UserProfile('@grimReapr')
	#up.share() # >> Sharing grimReapr

	'''movie = Movie('Star Trek Beyond')
	movie.share() # >> AttributeError'''

		
		