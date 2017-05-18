'''
An example to showcase decorater pattern using Composition with Contracts.
We attempt to create models for a simple version of LOTR flavored RPG game
Inspired from https://medium.com/jeremy-codes/decorator-pattern-in-swift-e5fa11ea3c3f
'''
from contracts_core import Contract, required, borrow

class Character(object):

	@required
	def getHealth(self): pass

class CharacterType(object):

	__reqdattribs__ = dict(base=Character)

@Contract(Character)
class Orc(object):
	'''
	Even though Orc is not of type Character, i.e., does not Inherit from Character,
	an instance of Orc will still pass as 'base' inside __reqdattribs__ check of
	CharacterType Contract. This demonstrates association/dependency agnosticism when
	it comes to Contract binding checks
	'''

	def getHealth(self): return 10

@Contract(Character)
class Human(object):

	def getHealth(self): return 25


class Elf(Character):
	'''
	Just for the sake of showcasing Association(Inheritence v/s Contract Binding) agnosticism when it comes to
	Contracts binding check, i.e., __reqdattribs__ check of CharacterType Contract passes because Elf happens to 
	be associated with Character - In this case via Inheritence
	'''

	#Not obligated to provide getHealth. Not providing this method will result in
	#ContractRequiredMethodInvokedError which is expected, since Elf subclasses Character
	def getHealth(self):
		return 5

@Contract(CharacterType, Character)
class Warlord(object):

	def __init__(self, base):
		self.base = base

	def getHealth(self):
		return self.base.getHealth() + 50

@Contract(CharacterType, Character)
class Epic(object):

	def __init__(self, base):
		self.base = base

	def getHealth(self):
		return self.base.getHealth() + 75

if __name__ == '__main__':
	
	orc = Orc()
	print orc.getHealth() # >>> 10

	orcWarlord = Warlord(orc)
	print orcWarlord.getHealth() # >>> 60

	epicOrc = Epic(orc)
	print epicOrc.getHealth() # >>> 85

	elf = Elf()
	print elf.getHealth() # >>> 5

	epicElf = Epic(elf)
	print epicElf.getHealth() # >>> 80

