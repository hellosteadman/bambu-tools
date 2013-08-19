# encoding: utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.conf import settings
from bambu.signup.models import EmailValidation

class RegistrationForm(forms.Form):
	first_name = forms.CharField(max_length = 20)
	last_name = forms.CharField(max_length = 20)
	email = forms.EmailField(label = _('Email address'))
	
	username = forms.RegexField(
		label = _('Username'), max_length = 30, regex = r'^[\w.@+-]+$',
		help_text = _('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
		error_messages = {
			'invalid': _('This value may contain only letters, numbers and @/./+/-/_ characters.')
		},
		widget = forms.TextInput(
			attrs = {
				'autocomplete': 'off'
			}
		)
	)
	
	password1 = forms.CharField(
		label = _('Password'),
		widget = forms.PasswordInput(
			attrs = {
				'autocomplete': 'off'
			}
		)
	)
	
	password2 = forms.CharField(label = _('Confirm password'),
		widget = forms.PasswordInput(
			attrs = {
				'autocomplete': 'off'
			}
		),
		help_text = _('Enter the same password as above, for verification.')
	)
	
	def clean_username(self):
		username = self.cleaned_data['username']
		
		try:
			User.objects.get(username__iexact = username)
		except User.DoesNotExist:
			return username.lower()
		
		raise forms.ValidationError(
			_('A user with that username already exists.')
		)
	
	def clean_password2(self):
		password1 = self.cleaned_data.get('password1', '')
		password2 = self.cleaned_data['password2']
		
		if password1 != password2:
			raise forms.ValidationError(
				_('The two password fields don\'t match.')
			)
		
		return password2
	
	def clean_email(self):
		email = self.cleaned_data['email']

		try:
			User.objects.get(email__iexact = email)
		except User.DoesNotExist:
			return email
		
		raise forms.ValidationError(
			_('A user with that email address already exists.')
		)
	
	def save(self, commit = True, next = None):
		user = User.objects.create_user(
			username = self.cleaned_data['username'],
			password = self.cleaned_data['password1'],
			email = self.cleaned_data['email']
		)
		
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		user.save()
		user.email_validations.create(next_url = next)
		
		return authenticate(
			username = self.cleaned_data['username'],
			password = self.cleaned_data['password1']
		)

class AuthenticationForm(forms.Form):
	username = forms.RegexField(
		label = _('Username'), max_length = 30, regex = r'^[\w.@+-]+$'
	)
	
	password = forms.CharField(label = _('Password'), widget = forms.PasswordInput)
	
	def clean(self):
		self._user_cache = authenticate(
			username = self.cleaned_data['username'],
			password = self.cleaned_data['password']
		)
		
		if not self._user_cache:
			raise forms.ValidationError('Please enter the correct username and password.')
		
		return self.cleaned_data
	
	def login(self, request):
		login(request, self._user_cache)
		return self._user_cache

class PasswordResetForm(forms.Form):
	email = forms.EmailField(label = _('Email address'))

class EmailValidationForm(forms.Form):
	code = forms.CharField(max_length = 10, label = u'Verification code')
	
	def __init__(self, *args, **kwargs):
		self.instance = kwargs.pop('instance')
		super(EmailValidationForm, self).__init__(*args, **kwargs)
	
	def clean_code(self):
		if self.cleaned_data.get('code') != self.instance.code:
			raise forms.ValidationError('That code is not correct.')