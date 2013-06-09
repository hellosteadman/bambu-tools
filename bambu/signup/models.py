from django.db import models
from django.contrib.auth.models import User
from bambu.mail import render_to_mail
from uuid import uuid4
import random, string

class EmailValidation(models.Model):
	user = models.ForeignKey('auth.User', related_name = 'email_validations', unique = True)
	next_url = models.CharField(max_length = 200, null = True, blank = True)
	guid = models.CharField(max_length = 36, unique = True)
	code = models.CharField(max_length = 10)
	sent = models.DateTimeField(auto_now_add = True)
	
	def __unicode__(self):
		return self.guid
	
	def save(self, *args, **kwargs):
		if not self.guid:
			self.guid = unicode(uuid4())
		
		if not self.code:
			self.code = ''.join(
				random.sample(string.letters + string.digits, 10)
			).upper()
		
		new = not self.pk
		super(EmailValidation, self).save(*args, **kwargs)
		
		self.user.is_active = False
		self.user.save()
		
		if new:
			render_to_mail(
				subject = u'Please confirm your email address',
				template = 'signup/mail/validate.txt',
				context = {
					'name': self.user.first_name or self.user.username,
					'guid': self.guid,
					'code': self.code,
					'next': self.next_url
				},
				recipient = self.user
			)
	
	class Meta:
		ordering = ('-sent',)
		get_latest_by = 'sent'

class PasswordReset(models.Model):
	user = models.ForeignKey(User, related_name = 'password_resets', unique = True)
	guid = models.CharField(max_length = 36, unique = True)
	next_url = models.CharField(max_length = 200, null = True, blank = True)
	sent = models.DateTimeField(auto_now_add = True)
	
	def __unicode__(self):
		return self.guid
	
	def save(self, *args, **kwargs):
		if not self.guid:
			self.guid = unicode(uuid4())
		
		new = not self.pk
		super(PasswordReset, self).save(*args, **kwargs)
		
		if new:
			render_to_mail(
				subject = u'Forgotten your password?',
				template = 'signup/mail/password-reset.txt',
				context = {
					'name': self.user.first_name or self.user.username,
					'guid': self.guid,
					'next': self.next_url
				},
				recipient = self.user
			)
	
	def reset(self):
		password = User.objects.make_random_password(10)
		
		self.user.set_password(password)
		self.user.save()
		self.delete()
		
		render_to_mail(
			subject = u'Your new password',
			template = 'signup/mail/password.txt',
			context = {
				'name': self.user.first_name or self.user.username,
				'username': self.user.username,
				'password': password,
				'next': self.next_url
			},
			recipient = self.user
		)
	
	class Meta:
		ordering = ('-sent',)
		get_latest_by = 'sent'