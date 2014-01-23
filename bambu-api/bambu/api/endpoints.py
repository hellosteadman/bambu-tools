"""
Exposes API endpoints for the :class:`django.contrib.auth.models.User` and
:class:`django.contrib.auth.models.Group` models.
"""

from django.contrib.auth.models import User, Group
from django.contrib.webdesign import lorem_ipsum
from django.conf.urls import patterns, url
from django.conf import settings
from django.db import models, transaction
from bambu import api
from bambu.api import helpers
from bambu.api.forms import UserRegistrationForm
from bambu.api.auth.decorators import anonymous

ALLOW_REGISTRATION = getattr(settings, 'API_AUTH_ALLOW_REGISTRATION', False)
ALLOW_USER_MANAGEMENT = getattr(settings, 'API_ALLOW_USER_MANAGEMENT', False)
ALLOW_GROUP_MANAGEMENT = getattr(settings, 'API_ALLOW_GROUP_MANAGEMENT', False)

if ALLOW_USER_MANAGEMENT:
	class UserAPI(api.ModelAPI):
		"""
		Create, read, update and delete user accounts.
		"""

		fields = ('id', 'username', 'first_name', 'last_name')
		app_label_verbose = 'Users and groups'

		def get_urls(self):
			urlpatterns = super(UserAPI, self).get_urls()
	
			urlpatterns += patterns('',
				url(r'login\.(?P<format>' + '|'.join(self.allowed_formats) + ')$',
					helpers.wrap_api_function(
						self.api_site,
						self.login_view,
						1,
						('GET',),
						self.prepare_output_data
					)
				)
			)
	
			if ALLOW_REGISTRATION:
				urlpatterns += patterns('',
					url(r'unregister\.(?P<format>' + '|'.join(self.allowed_formats) + ')$',
						helpers.wrap_api_function(
							self.api_site,
							self.unregister_view,
							1,
							('POST',),
							self.prepare_output_data
						)
					),
					url(r'register\.(?P<format>' + '|'.join(self.allowed_formats) + ')$',
						helpers.wrap_api_function(
							self.api_site,
							self.register_view,
							1,
							('POST',),
							self.prepare_output_data
						)
					)
				)
	
			return urlpatterns
		
		@api.argument('format', 'str', u'The data format to return')
		def login_view(self, request):
			return request.user

		@anonymous
		@transaction.commit_on_success
		@api.argument('format', 'str', u'The data format to return')
		def register_view(self, request):
			form = UserRegistrationForm(request.POST)
			if form.is_valid():
				return form.save()
			else:
				raise Exception(dict(form.errors.items()))
		
		@transaction.commit_on_success
		@api.argument('format', 'str', u'The data format to return')
		def unregister_view(self, request):
			request.user.delete()
			return True
	
	api.site.register(User, UserAPI)
	
	if ALLOW_GROUP_MANAGEMENT:
		class GroupAPI(api.ModelAPI):
			"""
			Create, read, update and delete user groups.
			"""

			fields = ('id', 'name')
			allowed_methods = ('GET',)
	
		api.site.register(Group, GroupAPI)