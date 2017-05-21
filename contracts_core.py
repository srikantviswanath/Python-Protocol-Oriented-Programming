'''
The core logic that handles all the magic under the hood
'''

def Contract(*Conformers):

	def ContractDecorator(Conformee):

		class ContractWrapper(Conformee):
			'''
			This class intercepts the instantiation of Conformee class - to do it's Contract magic, i.e., 
			check adherence to Contract blueprint. If successful, inject methods decorated with @borrow keyword
			into the scope of an instance of Conformee class
			'''

			def __init__(self, *args):
				self.missingReqdMethods = dict()
				self.conformee = Conformee(*args)
				reqdVals = map(lambda x: x.__reqdattribs__.items() if '__reqdattribs__' in x.__dict__ else list(), Conformers)
				reqdVals = [item for sublist in reqdVals for item in sublist]

				missingAttribs = self._missingAttribsValidator(reqdVals)
				if missingAttribs:
					raise ContractBreakError(Conformee.__name__, Conformers, list(missingAttribs), 1)

				typeMismatch = self._attribsTypeValidator(reqdVals)
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
				'''
				Validator method to validate the presence of attributes mentioned in Contract's __reqdattribs__
				within the scope of Conformee's instance
				'''
				return set(map(lambda x: x[0], reqdVals)) - set(self.conformee.__dict__.keys())

			def _attribsTypeValidator(self, reqdVals):
				'''
				Validator method to validate Contract's binding w.r.t to __reqdattribs__. It checks for 
				each attribute mentioned in __reqdattribs__ to have some kind of association with the type
				specified. Association can mean Type inheritence or Contract binding
				'''
				return filter(
					lambda x: not isinstance(self.conformee.__dict__[x[0]], x[1]) and \
						x[1] not in (self.conformee.__dict__[x[0]].__class__.__protocols__ \
							if hasattr(self.conformee.__dict__[x[0]].__class__, '__protocols__') else list()), reqdVals
				)

		return ContractWrapper
	return ContractDecorator


def required(method):
	'''
	decorator to deem a method of Contract class as a mandatory method, intended to be implemented
	by the conformee class abiding by the Contract

	:param function method:
	'''

	def requiredWrapper(self, *args):
		raise ContractRequiredMethodInvokedError(method, self)
	return requiredWrapper

extensionRegistry = dict()
def borrow(*dependencies):
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
			return extensionRegistry[tuple((matchingDep, methodMetaKey))](self, *args)
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

class ContractBreakError(Exception):
	commonError = 'Class {conformingClass} does not abide by Contracts: {contracts}.'
	errorMsgDict = {
		1: commonError + 'Following required attributes are missing: \n {errorElements}',
		2: commonError + 'Following attributes have types mismatch: \n {errorElements}',
		3: commonError + 'Following required methods are missing: \n {errorElements}'
	}
	
	def __init__(self, conformee, contracts, missingElements, enum):
		super(ContractBreakError, self).__init__(
			self.errorMsgDict[enum].format(
				conformingClass = conformee,
				contracts = contracts,
				errorElements = missingElements
			)
		)

class ContractRequiredMethodInvokedError(Exception):
	errorMsg = 'Required method {method} of Contract {contract} invoked. This is only meant to be invoked by abiding classes'

	def __init__(self, method, contract):
		super(ContractRequiredMethodInvokedError, self).__init__(
			self.errorMsg.format(
				method = method,
				contract = contract.__name__
			)
		)