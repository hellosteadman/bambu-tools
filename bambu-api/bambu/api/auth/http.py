from django.contrib.auth import authenticate
from django.template.response import TemplateResponse
from django.conf import settings
from bambu.api.auth import AuthenticationBase

class HTTPAuthentication(AuthenticationBase):
	"""
	Access to the API is granted via HTTP Basic Authentication. If you don't already have
	a username and password, you'll need to sign up for one. You can read the
	`Wikipedia article on HTTP Basic Authentication
	<http://en.wikipedia.org/wiki/Basic_access_authentication/>`_
	for more details.
	"""
	
	verbose_name = 'HTTP authentication'
	
	def authenticate(self, request):
		auth = request.META.get('HTTP_AUTHORIZATION')
		if not auth:
			return False
		
		method, auth = auth.split(' ', 1)
		if method.lower() != 'basic':
			return False
		
		auth = auth.strip().decode('base64')
		username, password = auth.split(':', 1)
		self.user = authenticate(
			username = username,
			password = password
		)
		
		return not self.user is None
	
	def challenge(self, request):
		realm = getattr(settings, 'API_AUTH_REALM', 'Restricted access')
		response = TemplateResponse(
			request,
			'api/401.html'
		)
		
		response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
		response.status_code = 401
		return response