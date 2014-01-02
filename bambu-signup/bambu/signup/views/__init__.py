from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.importlib import import_module
from django.utils.http import urlencode
from django.conf import settings
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect
from bambu.signup.models import *

SIGNUP_FORM = getattr(settings, 'SIGNUP_FORM', 'bambu.signup.forms.RegistrationForm')
LOGIN_FORM = getattr(settings, 'LOGIN_FORM', 'bambu.signup.forms.AuthenticationForm')
LOGIN_URL = getattr(settings, 'LOGIN_URL')
VALIDATION_FORM = getattr(settings, 'SIGNUP_VALIDATION_FORM', 'bambu.signup.forms.EmailValidationForm')
PASSWORD_RESET_FORM = getattr(settings, 'PASSWORD_RESET_FORM', 'bambu.signup.forms.PasswordResetForm')
LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '/')
LOGOUT_REDIRECT_URL = getattr(settings, 'LOGOUT_REDIRECT_URL', '/')

def _get_form(constant):
	module, dot, klass = constant.rpartition('.')
	module = import_module(module)
	return getattr(module, klass)

def register(request):
	if request.user.is_authenticated():
		messages.warning(request, u'You already have an account.')
		return HttpResponseRedirect(LOGIN_REDIRECT_URL)
	
	form_class = _get_form(SIGNUP_FORM)
	form = form_class(data = request.POST or None)
	next = request.POST.get('next',
		request.GET.get('next',
			LOGIN_REDIRECT_URL
		)
	)
	
	if request.method == 'POST' and form.is_valid():
		user = form.save(next = next)
		auth_login(request, user)
		
		return HttpResponseRedirect(
			reverse('signup_complete')
		)
	
	return TemplateResponse(
		request,
		'signup/register.html',
		{
			'form': form,
			'next': next
		}
	)

def register_complete(request):
	return TemplateResponse(
		request,
		'signup/complete.html',
		{
			'next': next
		}
	)

def login(request):
	form_class = _get_form(LOGIN_FORM)
	form = form_class(request.POST or None)
	
	if request.method == 'POST' and form.is_valid():
		if form.login(request):
			return HttpResponseRedirect(
				request.GET.get('next', LOGIN_REDIRECT_URL)
			)
	
	return TemplateResponse(
		request,
		'signup/login.html',
		{
			'form': form
		}
	)
	
def logout(request):
	auth_logout(request)
	messages.success(request, u'You have been logged out.')
	return HttpResponseRedirect(LOGOUT_REDIRECT_URL)

@transaction.commit_on_success
def verify_email(request, guid):
	validation = get_object_or_404(EmailValidation, guid = guid)
	next = validation.next_url
	form_class = _get_form(VALIDATION_FORM)
	form = form_class(data = request.POST or None, instance = validation)
	
	if request.method == 'POST' and form.is_valid():
		validation.user.is_active = True
		validation.user.save()
		validation.delete()
		messages.success(request,
			_('Thanks for confirming your email address.')
		)
		
		return HttpResponseRedirect(
			'%s?%s' % (
				LOGIN_URL,
				urlencode(
					{
						'next': next or LOGIN_REDIRECT_URL
					}
				)
			)
		)
	
	return TemplateResponse(
		request,
		'signup/validation.html',
		{
			'form': form
		}
	)

def reset_password(request, guid = None):
	next = request.POST.get('next', request.GET.get('next'))
	
	if guid:
		reset = get_object_or_404(PasswordReset, guid = guid)
		reset.reset()
		
		messages.success(request,
			_('Your new password should be in your inbox shortly.')
		)
		
		return HttpResponseRedirect(settings.LOGIN_URL)
	
	form_class = _get_form(PASSWORD_RESET_FORM)
	form = form_class(request.POST or None)
	
	if request.method == 'POST' and form.is_valid():
		with transaction.commit_on_success():
			try:
				user = User.objects.get(email__iexact = form.cleaned_data['email'])
				if not user.password_resets.exists():
					reset = user.password_resets.create(
						next_url = next
					)
			except User.DoesNotExist:
				pass
		
		return TemplateResponse(
			request,
			'signup/password-reset.html'
		)
	
	return TemplateResponse(
		request,
		'signup/forgot-password.html',
		{
			'form': form
		}
	)
