from copy import copy

class ProviderBase(object):
	def __init__(self, **kwargs):
		self.settings = copy(kwargs)
	
	def subscribe(self, email, **kwargs):
		raise NotImplementedError('Method not implemented.')
	
	def map_args(self, action, **kwargs):
		mappings = self.settings.get('ARG_MAPPING', {})
		result = [
			kwargs.get(mapping)
			for mapping in mappings.get(action)
		]
		
		while len(result) > 0 and result[-1] is None:
			result.pop()
		
		return result