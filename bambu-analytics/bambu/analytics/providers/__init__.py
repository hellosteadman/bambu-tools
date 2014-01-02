from copy import copy
from django.contrib.sites.models import Site

class ProviderBase(object):
	def __init__(self, **kwargs):
		self.events = []
		self.settings = copy(kwargs)
		self.site = Site.objects.get_current()
	
	def track(self, event, **kwargs):
		raise NotImplementedError('Method not implemented.')
	
	def render(self, request):
		raise NotImplementedError('Method not implemented.')