from django.db import models
from django.db.models import F
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.http import urlencode
from bambu.api.managers import *
from bambu.api import helpers
from datetime import datetime, timedelta
from time import time

REQUEST_LOGGER = helpers.get_request_logger()

class App(models.Model):
	admin = models.ForeignKey(User, related_name = 'owned_apps')
	name = models.CharField(max_length = 50)
	description = models.TextField()
	key = models.CharField(max_length = 18, editable = False)
	secret = models.CharField(max_length = 32, editable = False)
	status = models.PositiveIntegerField(default = 1, editable = False,
		choices = (
			(1, u'accepted'),
		)
	)
	
	callback_url = models.URLField(u'callback URL', max_length = 255, null = True, blank = True)
	deployment = models.CharField(
		max_length = 1, default = '',
		choices = (
			('w', u'Web'),
			('m', u'Mobile'),
			('d', u'Desktop')
		)
	)
	
	http_login = models.BooleanField(u'allow login via HTTP')
	http_signup = models.BooleanField(u'allow signup via HTTP')
	
	def __unicode__(self):
		return self.name
		
	def clean(self):
		if self.deployment == 'w' and not self.callback_url:
			raise ValidationError('A callback URL is required for web applications.')
	
	def save(self, *args, **kwargs):
		if not self.key and not self.secret:
			key = helpers.generate_random_key(18)
			secret = helpers.generate_random_key(32)
			
			while App.objects.filter(key__exact = key, secret__exact = secret).exists():
				secret = helpers.generate_random_key(32)
			
			self.key = key
			self.secret = secret
		
		super(App, self).save(*args, **kwargs)
	
	def log_request(self):
		if REQUEST_LOGGER.validate_request(self):
			REQUEST_LOGGER.log_request(self)
			return True
		else:
			return False
	
	@property
	def users(self):
		return User.objects.filter(
			pk__in = self.tokens.filter(user__isnull = False, token_type = 2).values_list('user',
				flat = True
			)
		)
	
	class Meta:
		ordering = ('name',)

class Nonce(models.Model):
	token_key = models.CharField(max_length = 18)
	consumer_key = models.CharField(max_length = 32)
	key = models.CharField(max_length = 255)
	
	def __unicode__(self):
		return u'Nonce %s for %s' % (self.key, self.consumer_key)

class Token(models.Model):
	key = models.CharField(max_length = 18)
	secret = models.CharField(max_length=32)
	verifier = models.CharField(max_length = 10)
	token_type = models.PositiveIntegerField(choices = 
		(
			(1, u'Request'),
			(2, u'Access')
		)
	)
	
	timestamp = models.PositiveIntegerField(default = long(time()))
	approved = models.BooleanField(default = False)
	
	user = models.ForeignKey(User, null = True, blank = True, related_name = 'tokens')
	app = models.ForeignKey(App, related_name = 'tokens')
	callback = models.CharField(max_length = 255, null=True, blank = True)
	callback_confirmed = models.BooleanField(default = False)
	
	objects = TokenManager()
	
	def __unicode__(self):
		return u'%s Token %s for %s' % (
			self.get_token_type_display(), self.key, self.app
		)
	
	def to_string(self, only_key = False):
		token_dict = {
			'oauth_token': self.key, 
			'oauth_token_secret': self.secret,
			'oauth_callback_confirmed': 'true',
		}
		
		if self.verifier:
			token_dict['oauth_verifier'] = self.verifier
		
		if only_key:
			del token_dict['oauth_token_secret']
		
		return urlencode(token_dict)
	
	def save(self, *args, **kwargs):
		if not self.key and not self.secret:
			key = helpers.generate_random_key(18)
			secret = helpers.generate_random_key(32)
			
			while Token.objects.filter(
				key__exact = key, secret__exact = secret
			).exists():
				secret = helpers.generate_random_key(32)
			
			self.key = key
			self.secret = secret
		
		super(Token, self).save(*args, **kwargs)
	
	def get_callback_url(self):
		if self.callback and self.verifier:
			parts = urlparse.urlparse(self.callback)
			scheme, netloc, path, params, query, fragment = parts[:6]
			
			if query:
				query = '%s&oauth_verifier=%s' % (query, self.verifier)
			else:
				query = 'oauth_verifier=%s' % self.verifier
			
			return urlparse.urlunparse((scheme, netloc, path, params,
				query, fragment))
		
		return self.callback
	
	def set_callback(self, callback):
		if callback != 'oob':
			self.callback = callback
			self.callback_confirmed = True
			self.save()

class RequestBatch(models.Model):
	app = models.ForeignKey(App, related_name = 'requests')
	timestamp = models.PositiveIntegerField(default = 0)
	count = models.PositiveIntegerField(default = 1)
	
	class Meta:
		unique_together = ('app', 'timestamp')