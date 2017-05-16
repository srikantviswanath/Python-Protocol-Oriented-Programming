'''
An example to depict the types-dependecy inference of protocol extensions.
Inspired by http://sam.dods.co/blog/2015/08/04/why-i-love-swift-protocol-extensions/
Thanks to Sam Dods
'''
from contracts_core import Contract, required, borrow

class MediaItem(object):

	copyRightsAgreement = 'Yet another lisencing agreement...'
	
	def __init__(self, filename):
		self.name = filename

class Sharable(object):

	__reqdattribs__ = dict(name=str)

	@borrow()
	def share(self):
		print 'Sharing {filename}'.format(filename=self.name)

	@borrow(MediaItem)
	def share(self):
		print 'Hoping you read thru the following lisence agreement:'
		print self.copyRightsAgreement
		print 'Sharing...'

@Contract(Sharable)
class AudioClip(MediaItem):

	def __init__(self, filename):
		self.__class__.__base__.__init__(self, filename) #Workaround for super()
		#super(AudioClip, self).__init__(filename) -> TODO: Need to fix this. 
		#Using super throws TypeError: super(type, obj): obj must be an instance or subtype of type
		#Due to Class reloads

@Contract(Sharable)
class UserProfile(object):

	def __init__(self, profilename):
		self.name = profilename


class Movie(MediaItem):
	
	def __init__(self, filename):
		super(Movie, self).__init__(filename)
		

@Contract(Sharable)
class Image(MediaItem):
	
	def __init__(self, filename):
		self.__class__.__base__.__init__(self, filename)


if __name__ == '__main__':
	ac = AudioClip('coldplay_01.wav')
	ac.share() # >>'Hoping you read thru the following lisence agreement:'

	img = Image('picaso_01.jpg')
	img.share() # >> 'Hoping you read thru the following lisence agreement:'

	up = UserProfile('grimReapr')
	up.share() # >> Sharing grimReapr

	movie = Movie('Star Trek Beyond')
	movie.share() # >> AttributeError

		
		