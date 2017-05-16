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
								if v.func_name == 'required':
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