'''
The core logic that handles all the magic under the hood
'''

def Contract(*Conformers):

	def ContractDecorator(Conformee):

		class ContractWrapper(Conformee):

			def __init__(self, *args):
				self.missingReqdMethods = dict()
				self.conformee = Conformee(*args)
				reqdVals = map(lambda x: x.__reqdattribs__.items() if '__reqdattribs__' in x.__dict__ else list(), Conformers)
				reqdVals = [item for sublist in reqdVals for item in sublist]

				missingAttribs = self.missingAttribsValidator(reqdVals)
				if missingAttribs:
					raise ContractBreakError(Conformee._name__, Conformers, list(missingAttribs), 1)

				typeMismatch = self.attribsTypeValidator(reqdVals)
				if typeMismatch:
					raise ContractBreakError(Conformee.__name__, Conformers, list(typeMismatch), 2)

				map(lambda x: self.__dict__.update({x[0]: x[1]}), self.conformee.__dict__.items())

				for ConformerClass in Conformers:
					self.missingReqdMethods[ConformerClass.__name__] = list()
					for k, v in ConformerClass.__dict__.iteritems():
						if callable(v):
							if k not in Conformee.__dict__:
								if v.func_name == 'requiredWrapper':
									self.missingReqdMethods[ConformerClass.__name__].extend(['{method}()'.format(method=k)])
								if v.func_name == 'borrowWrapper' and k not in Conformee.__dict__:
									setattr(self.__class__, k, v)
				nonConformers = filter(lambda x: x[1], self.missingReqdMethods.items())
				if nonConformers:
					raise ContractBreakError(Conformee.__name__, map(lambda x: x[0], nonConformers), nonConformers, 3)
				setattr(self.__class__, '__protocols__', Conformers)

			def _missingAttribsValidator(self, reqdVals):
				return set(map(lambda x: x[0], reqdVals)) - set(self.conformee.__dict__.keys())

			def attribsTypeValidator(self, reqdVals):
				return filter(lambda x: not isinstance(self.conformee.__dict__[x[0]], x[1]), reqdVals)

		return ContractWrapper
	return ContractDecorator


def required(method):
	'''
	decorator to deem a method of Contract class as a mandatory method, intended to be implemented
	by the conformee class abiding by the Contract

	:param function method:
	'''

	def requiredWrapper(self, *args):
		raise ContractRequiredMethodInvoked(method, self)
	return required

extensionRegistry = dict()
def borrow(*dpeendencies):
	'''
	decorator to deem an instance method of Contract class to be borrowed by abiding Conformee classes.
	i.e., This is the place to implement common functionality for all conforming classes ala Swift protocol extensions

	:param tuple(<type>) dependencies: These are used to profide default implementations based on type-dependency 
										inference for multidispatch of methods
	'''
	def borrowDecorator(method):
		methodMetaKey = method.__module__ + ':' + method.__name__
		regKey = tuple((tuple(map(lambda x: x.__name__, dependencies or tuple((object, )))), methodMetaKey))
		if regKey in extensionRegistry:
			pass #TODO: Log duplicate registration
		extensionRegistry[regKey] = method
		def borrowWrapper(self, *args):
			objDeps = map(lambda x: x.__name__, self.__protocols__)
			objDeps.extend([self.__class__.__base__.__base__.__name__])
			matchingDep = _bestFit(objDeps)
			return extensionRegistry[tuple((matchingDep, methodMetaKey))][self, *args]
		return borrowWrapper
	return borrowDecorator

def _bestFit(conformeeDeps):
	'''
	helper function determine the best type bundle fit amongst a bunch of type registrations registered
	at global dictionary extensionRegistry

	:param tuple(<type>) conformeeDeps: The actual dependecies of the Conformee class, i.e, parent classes and 
										protocol classes
	'''
	default = tuple((object.__name__, ))
	match = default
	for k in extensionRegistry:
		k = k[0]
		if set(k).issubset(set(conformeeDeps)):
			if len(k) == len(match):
				if match != default:
					match = default
				else: 
					match = k
			elif len(k) > len(match):
				match = k
	return match