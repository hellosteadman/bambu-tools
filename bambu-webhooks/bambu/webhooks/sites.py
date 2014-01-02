class AlreadyRegistered(Exception):
	pass

class NotRegistered(Exception):
	pass
	
class WebHookSite():
	_registry = {}
	
	def register(self, name, verbose_name = None, **kwargs):
		if name in self._registry:
			raise AlreadyRegistered('Hook %s already registered.' % name)
		
		if not verbose_name:
			verbose_name = name.replace('_', ' ').capitalize()
		
		kwargs['verbose_name'] = verbose_name
		self._registry[name] = kwargs