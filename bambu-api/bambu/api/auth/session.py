from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from bambu.api.auth import AuthenticationBase

class DjangoSessionAuthentication(AuthenticationBase):
	"""
	Access to the API is granted via this website's login page.
	"""
	
	verbose_name = 'Website authentication'
	
	def authenticate(self, request):
		self.user = None
		
		if request.user.is_authenticated():
			self.user = request.user
		
		return not self.user is None
	
	def challenge(self, request):
		return HttpResponseRedirect(
			getattr(settings, 'API_LOGIN_URL',
				reverse('login')
			)
		)