from bambu.api.auth import AuthenticationBase
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.conf.urls import patterns, url
from django.template.response import TemplateResponse
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from oauth.oauth import OAuthRequest, OAuthServer, OAuthDataStore, OAuthError
from oauth.oauth import OAuthSignatureMethod_PLAINTEXT
from bambu.api.models import Nonce, Token, App
from bambu.api.helpers import generate_random_key, send_oauth_error

class DataStore(OAuthDataStore):
	def __init__(self, request):
		self.signature = request.parameters.get('oauth_signature', None)
		self.timestamp = request.parameters.get('oauth_timestamp', None)
		self.scope = request.parameters.get('scope', 'all')
	
	def lookup_consumer(self, key):
		try:
			self.consumer = App.objects.get(key = key)
			return self.consumer
		except App.DoesNotExist:
			pass
	
	def lookup_token(self, token_type, token):
		if token_type == 'request':
			token_type = 1
		elif token_type == 'access':
			token_type = 2
		
		try:
			self.request_token = Token.objects.get(
				key = token, 
				token_type = token_type
			)
			
			return self.request_token
		except Token.DoesNotExist:
			pass
	
	def lookup_nonce(self, oauth_consumer, oauth_token, nonce):
		if not oauth_token is None:
			nonce, created = Nonce.objects.select_for_update().get_or_create(
				consumer_key = oauth_consumer.key, 
				token_key = oauth_token.key,
				key = nonce
			)
			
			if not created:
				return nonce.key
	
	def fetch_request_token(self, oauth_consumer, oauth_callback):
		if oauth_consumer.key == self.consumer.key:
			self.request_token = Token.objects.create_token(
				app = self.consumer,
				token_type = 1,
				timestamp = self.timestamp
			)
			
			if oauth_callback:
				self.request_token.set_callback(oauth_callback)
			
			return self.request_token
	
	def fetch_access_token(self, oauth_consumer, oauth_token, oauth_verifier):
		if oauth_consumer.key == self.consumer.key \
		and oauth_token.key == self.request_token.key \
		and oauth_verifier == self.request_token.verifier \
		and self.request_token.approved:
			self.access_token = Token.objects.create_token(
				app = self.consumer,
				token_type = 2,
				timestamp = self.timestamp,
				user = self.request_token.user
			)
			
			return self.access_token

	def authorize_request_token(self, oauth_token, user):
		if oauth_token.key == self.request_token.key:
			self.request_token.approved = True
			self.request_token.user = user
			self.request_token.verifier = generate_random_key(10)
			self.request_token.save()
			
			return self.request_token

def initialise_server_request(request):
	if request.method == "POST":
		params = dict(request.REQUEST.items())
	else:
		params = {}
	
	request.META['Authorization'] = request.META.get('HTTP_AUTHORIZATION', '')
	oauth_request = OAuthRequest.from_request(
		request.method, request.build_absolute_uri(), 
		headers = request.META, parameters = params,
		query_string = request.environ.get('QUERY_STRING', '')
	)
	
	if oauth_request:
		oauth_server = OAuthServer(DataStore(oauth_request))
		oauth_server.add_signature_method(OAuthSignatureMethod_PLAINTEXT())
	else:
		oauth_server = None
		
	return oauth_server, oauth_request

class AuthoriseForm(AuthenticationForm):
	pass

class OAuthAuthentication(AuthenticationBase):
	"""
	Access to the API is granted via the OAuth protocol. You'll need to
	`create an app
	</develop/apps/>`_ in order to use the API. You can read the
	`Wikipedia article on OAuth
	<http://en.wikipedia.org/wiki/OAuth/>`_ for more details.
	"""
	
	verbose_name = 'OAuth'
	app_model = 'api.App'
	
	def get_urls(self):
		return patterns('',
			url(r'^request-token/$', self.request_token_view),
			url(r'^authorise/$', self.authorise_view),
			url(r'^access-token/$', self.access_token_view)
		)
	
	def validate_request(self, request):
		must_have = [
			'oauth_%s' % s for s in [
				'consumer_key', 'token', 'signature',
				'signature_method', 'timestamp', 'nonce'
			]
		]
		
		is_in = lambda l: all([(p in l) for p in must_have])
		
		auth_params = request.META.get('HTTP_AUTHORIZATION', '')
		req_params = request.REQUEST
		
		return is_in(auth_params) or is_in(req_params)
	
	def authenticate(self, request):
		if self.validate_request(request):
			try:
				oauth_server, oauth_request = initialise_server_request(request)
				if oauth_server is None or oauth_request is None:
					return False
				
				consumer, token, parameters = oauth_server.verify_request(oauth_request)
			except OAuthError, ex:
				return False
			
			if consumer and token:
				self.user = token.user
				return True
		
		return False
	
	def request_token_view(self, request):
		oauth_server, oauth_request = initialise_server_request(request)
		
		if oauth_server is None:
			return send_oauth_error(
				OAuthError('Invalid request parameters.')
			)
		
		try:
			token = oauth_server.fetch_request_token(oauth_request)
			return HttpResponse(token.to_string())
		except OAuthError, ex:
			return send_oauth_error(ex)
	
	def authorise_view(self, request):
		oauth_server, oauth_request = initialise_server_request(request)
		
		if oauth_server is None or oauth_request is None:
			return send_oauth_error(
				OAuthError('Invalid request parameters.')
			)
		
		app = oauth_server._get_consumer(oauth_request)
		
		try:
			token = oauth_server.fetch_request_token(oauth_request)
		except OAuthError, ex:
			return send_oauth_error(ex)
		
		if request.method == 'GET':
			response = TemplateResponse(
				request,
				'api/auth/oauth/authorise.html',
				{
					'form': AuthoriseForm(),
					'app': app,
					'no_login_form': True,
					'popup': True
				}
			)
			
			response.status_code = 401
			response.realm = 'API'
			
			return response
		elif request.method == 'POST':
			callback = app.callback_url
			form = AuthoriseForm(data = request.POST)
			
			if request.user.is_authenticated():
				token = oauth_server.authorize_token(token, request.user)
				
				if callback:
					args = '?%s' % token.to_string(only_key = True)
					return HttpResponseRedirect(callback + args)
				else:
					return HttpResponse(token.to_string(only_key = True), mimetype = 'text/plain')
			elif form.is_valid():
				token = oauth_server.authorize_token(token, form.get_user())
				
				if callback:
					args = '?%s' % token.to_string(only_key = True)
					return HttpResponseRedirect(callback + args)
				else:
					return HttpResponse(token.to_string(only_key = True), mimetype = 'text/plain')
			else:
				response = TemplateResponse(
					request,
					'api/auth/oauth/authorise.html',
					{
						'form': form,
						'app': app,
						'no_login_form': True,
						'popup': True
					}
				)
				
				response.status_code = 401
				response.realm = 'API'
				return response
	
	def access_token_view(self, request):
		oauth_server, oauth_request = initialise_server_request(request)
		
		if oauth_request is None:
			return send_oauth_error(
				OAuthError('Invalid request parameters.')
			)
		
		try:
			token = oauth_server.fetch_access_token(oauth_request)
			return HttpResponse(token.to_string())
		except OAuthError, ex:
			return send_oauth_error(ex)