# encoding: utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.safestring import mark_safe
from bambu.payments import get_gateway_choices
from bambu.payments.models import Payment, TaxRate
from bambu.saas.models import Plan, UserPlan, UserPlanChange, Discount, Invitation
from bambu.saas.helpers import get_currency_symbol, format_price
from bambu.saas.fields import ImageChoiceField
from bambu.saas.signals import plan_subuser_added
from bambu.notifications import notify
import random

GATEWAYS = get_gateway_choices(True, False)

class RegistrationForm(forms.Form):
	first_name = forms.CharField(max_length = 20)
	last_name = forms.CharField(max_length = 20)
	email = forms.EmailField(label = _('Email address'))
	
	username = forms.RegexField(
		label = _('Username'), max_length = 30, regex = r'^[\w.@+-]+$',
		help_text = _('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
		error_messages = {
			'invalid': _('This value may contain only letters, numbers and @/./+/-/_ characters.')
		}
	)
	
	password1 = forms.CharField(label = _('Password'), widget = forms.PasswordInput)
	password2 = forms.CharField(label = _('Confirm password'), widget = forms.PasswordInput,
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
	
	def save(self, commit = True):
		user = User.objects.create_user(
			username = self.cleaned_data['username'],
			password = self.cleaned_data['password1'],
			email = self.cleaned_data['email']
		)

		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		
		if commit:
			user.save()
		
		return user

class SignupForm(RegistrationForm):
	plan = forms.ModelChoiceField(queryset = Plan.objects, empty_label = None)
	period = forms.ChoiceField(
		label = _(u'Billing frequency'),
		choices = (
			(1, _('Monthly')),
			(12, _('Annually'))
		),
		initial = 12,
		required = False
	)
	
	payment_gateway = ImageChoiceField(
		label = _('Pay via'),
		choices = any(GATEWAYS) and GATEWAYS or [],
		initial = any(GATEWAYS) and GATEWAYS[0][0] or None
	)
	
	discount_code = forms.CharField(
		max_length = 50, required = False,
		help_text = u'If you have a discount code, enter it here.'
	)
	
	def __init__(self, *args, **kwargs):
		currency = kwargs.pop('currency',
			getattr(settings, 'DEFAULT_CURRENCY', 'GBP')
		)
		
		self.challenge_words = kwargs.pop('challenge_words', None)
		super(SignupForm, self).__init__(*args, **kwargs)
		
		if Plan.objects.count() == 1:
			plan = Plan.objects.get(pk = settings.SAAS_DEFAULT_PLAN)
			del self.fields['plan']
		else:
			plan = Plan.objects.get(
				pk = self.initial.get('plan') or settings.SAAS_DEFAULT_PLAN
			)
		
		tax_rate = TaxRate.objects.get(
			chargeable_percent = settings.PAYMENTS_DEFAULT_TAXRATE
		)
		
		symbol = get_currency_symbol(currency)
		price = plan.prices.get(currency = currency)
		price_monthly = format_price(symbol, price.monthly)
		price_yearly = format_price(symbol, price.yearly)
		
		self.fields['period'].choices = (
			(1, _('Monthly (%s + %s)' % (price_monthly, tax_rate.shorthand))),
			(12, _('Annually (%s + %s)' % (price_yearly, tax_rate.shorthand)))
		)
		
		if getattr(settings, 'SAAS_NEWSLETTER_OPTIN', False):
			self.fields['newsletter_optin'] = forms.BooleanField(
				label = getattr(settings, 'SAAS_NEWSLETTER_OPTIN_PROMPT',
					u'Subscribe to our newsletter'
				),
				required = False,
				initial = True
			)
		
		if getattr(settings, 'SAAS_TERMS_URL', None):
			self.fields['terms'] = forms.BooleanField(
				label = mark_safe(
					u'I agree to be bound by the <a href="%s">terms and conditions</a>' % settings.SAAS_TERMS_URL
				)
			)
		
		if getattr(settings, 'SAAS_SIGNUP_CHALLENGE'):
			if self.challenge_words is None:
				right_words = settings.SAAS_SIGNUP_CHALLENGE.get('CORRECT_WORDS', [])
				wrong_words = settings.SAAS_SIGNUP_CHALLENGE.get('INCORRECT_WORDS', [])
				word_count = min(4, len(wrong_words))
				
				if word_count > 0:
					self.challenge_words = [random.choice(right_words)] + random.sample(wrong_words, word_count)
					random.shuffle(self.challenge_words)
			
			self.fields['challenge'] = forms.ChoiceField(
				label = settings.SAAS_SIGNUP_CHALLENGE.get('LABEL', u'Pick the correct word'),
				choices = [(w, w) for w in self.challenge_words],
			)
	
	def clean_discount_count(self):
		code = self.cleaned_data.get('discount_code')
		
		if code:
			try:
				discount = Discount.objects.get(code__iexact = code)
			except Discount.DoesNotExist:
				raise forms.ValidationError('No discount found for that code.')
		
		return ''
	
	def clean_challenge(self):
		right_words = settings.SAAS_SIGNUP_CHALLENGE.get('CORRECT_WORDS', [])
		if not self.cleaned_data.get('challenge') in right_words:
			raise forms.ValidationError(u'The correct answer was not given')
		
		return self.cleaned_data.get('challenge')
	
	def clean(self):
		period = self.cleaned_data.get('period') or 1
		code = self.cleaned_data.get('discount_code')
		
		if code:
			try:
				discount = Discount.objects.get(code__iexact = code)
				if not discount.valid_yearly and int(period) == 12:
					raise forms.ValidationError(
						u'This discount code is not available for annual subscriptions.'
					)
			except Discount.DoesNotExist:
				pass
		
		return self.cleaned_data
	
	def save(self, commit = True):
		user = super(SignupForm, self).save()
		
		plan = self.cleaned_data.get('plan',
			Plan.objects.get(pk = settings.SAAS_DEFAULT_PLAN),
		)
		
		if self.cleaned_data.get('discount_code'):
			discount = Discount.objects.get(
				code__iexact = self.cleaned_data['discount_code']
			)
		else:
			discount = None
		
		UserPlan.objects.create(
			user = user, plan = plan,
			period = int(self.cleaned_data.get('period') or 1),
			discount = discount
		)
		
		return authenticate(
			username = self.cleaned_data['username'],
			password = self.cleaned_data['password1']
		)

class PlanChangeForm(forms.Form):
	plan = forms.ModelChoiceField(queryset = Plan.objects, empty_label = None)
	period = forms.ChoiceField(
		label = _(u'Billing frequency'),
		choices = (
			(1, _('Monthly')),
			(12, _('Annually'))
		),
		initial = 12,
		required = False
	)
	
	payment_gateway = ImageChoiceField(
		label = _('Pay via'),
		choices = any(GATEWAYS) and GATEWAYS or (),
		initial = any(GATEWAYS) and GATEWAYS[0][0] or None
	)

	discount_code = forms.CharField(
		max_length = 50, required = False,
		help_text = u'If you have a discount code, enter it here.'
	)
	
	def __init__(self, *args, **kwargs):
		currency = kwargs.pop('currency',
			getattr(settings, 'DEFAULT_CURRENCY', 'GBP')
		)
		
		self.current_plan = kwargs.pop('current_plan')
		super(PlanChangeForm, self).__init__(*args, **kwargs)
		
		try:
			payment = self.current_plan.get_payment()
			del self.fields['payment_gateway']
			del self.fields['period']
		except Payment.DoesNotExist:
			pass
		
		self.fields['plan'].queryset = self.fields['plan'].queryset.exclude(
			pk = self.current_plan.plan.pk
		).filter(
			order__gte = self.current_plan.plan.order
		)
		
		plan = self.fields['plan'].queryset[0]
		tax_rate = TaxRate.objects.get(
			chargeable_percent = settings.PAYMENTS_DEFAULT_TAXRATE
		)
		
		symbol = get_currency_symbol(currency)
		price = plan.prices.get(currency = currency)
		price_monthly = format_price(symbol, price.monthly)
		price_yearly = format_price(symbol, price.yearly)
		
		if 'period' in self.fields:
			self.fields['period'].choices = (
				(1, _('Monthly (%s + %s)' % (price_monthly, tax_rate.shorthand))),
				(12, _('Annually (%s + %s)' % (price_yearly, tax_rate.shorthand)))
			)
	
	def clean_discount_count(self):
		code = self.cleaned_data.get('discount_code')
		
		if code:
			try:
				discount = Discount.objects.get(code__iexact = code)
			except Discount.DoesNotExist:
				raise forms.ValidationError('No discount found for that code.')
			
			if discount.filter(user_plan_changes__user = self.current_plan.user).exists():
				raise forms.ValidationError('You\'ve already used this discount code.')
			elif discount.filter(user_plans__user = self.current_plan.user).exists():
				raise forms.ValidationError('You\'ve already used this discount code.')
			
			return discount.code
		
		return ''
	
	def clean(self):
		period = self.cleaned_data.get('period') or 1
		code = self.cleaned_data.get('discount_code')
		
		if code:
			try:
				discount = Discount.objects.get(code__iexact = code)
				if not discount.valid_yearly and int(period) == 12:
					raise forms.ValidationError(
						u'This discount code is not available for annual subscriptions.'
					)
			except Discount.DoesNotExist:
				pass
		
		return self.cleaned_data
	
	def save(self, commit = True):
		new_plan = self.cleaned_data.get('plan')
		if self.cleaned_data.get('discount_code'):
			discount = Discount.objects.get(
				code__iexact = self.cleaned_data['discount_code']
			)
		else:
			discount = None
		
		change = UserPlanChange(
			user = self.current_plan.user,
			old_plan = self.current_plan.plan,
			new_plan = new_plan,
			discount = discount,
			period = int(self.cleaned_data.get('period') or self.current_plan.period)
		)
		
		currency = getattr(settings, 'DEFAULT_CURRENCY', 'GBP')
		price = new_plan.prices.get(currency = currency)
		
		if price.monthly == 0:
			change.paid = True
		
		change.save()
		return change

class PasswordResetForm(forms.Form):
	email = forms.EmailField(label = _('Email address'))

class ProfileForm(forms.ModelForm):
	first_name = forms.CharField(max_length = 20)
	last_name = forms.CharField(max_length = 20)
	email = forms.EmailField(label = _('Email address'))
	
	password1 = forms.CharField(
		label = _('Change password'), widget = forms.PasswordInput,
		required = False
	)
	
	password2 = forms.CharField(
		label = _('Confirm password'), widget = forms.PasswordInput,
		help_text = _('Enter the same password as above, for verification.'),
		required = False
	)
	
	def clean_password2(self):
		password1 = self.cleaned_data.get('password1', '')
		password2 = self.cleaned_data.get('password2', '')
		
		if password1 != password2:
			raise forms.ValidationError(
				_('The two password fields don\'t match.')
			)

		return password2
	
	def clean_email(self):
		email = self.cleaned_data['email']
		
		try:
			User.objects.exclude(pk = self.instance.pk).get(email__iexact = email)
		except User.DoesNotExist:
			return email
		
		raise forms.ValidationError(
			_('A user with that email address already exists.')
		)
	
	def save(self, commit = True):
		user = super(ProfileForm, self).save(commit = False)
		
		if self.cleaned_data.get('password1'):
			user.set_password(self.cleaned_data['password1'])
		
		if commit:
			user.save()
		
		return user
		
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email')

class InvitationsForm(forms.Form):
	emails = forms.CharField(widget = forms.Textarea)
	
	def __init__(self, *args, **kwargs):
		self.plan = kwargs.pop('plan')
		self.user = kwargs.pop('user')
		
		super(InvitationsForm, self).__init__(*args, **kwargs)
	
	def clean_emails(self):
		emails = self.cleaned_data.get('emails', '')
		
		for i, email in enumerate(emails.splitlines()):
			try:
				validate_email(email)
			except ValidationError:
				raise forms.ValidationError('The address on line %d is not valid' % (i + 1))
			
			if Invitation.objects.filter(email__iexact = email).exclude(plan = self.plan).exists():
				raise forms.ValidationError('The address on line %d has already been invited' % (i + 1))
			
			if User.objects.filter(email__iexact = email).exists():
				raise forms.ValidationError('The address on line %d is already registered to a site member' % (i + 1))
		
		return emails
	
	def save(self):
		invitations = []
		
		for email in self.cleaned_data.get('emails', '').splitlines():
			invitation, created = self.plan.invitations.get_or_create(
				email = email,
				sender = self.user
			)
			
			if not created:
				invitation.send()
			
			invitations.append(invitation)
		
		return invitations

class AcceptInvitationForm(RegistrationForm):
	def __init__(self, *args, **kwargs):
		self.plan = kwargs.pop('plan')
		super(AcceptInvitationForm, self).__init__(*args, **kwargs)
	
	def save(self, commit = True):
		user = super(AcceptInvitationForm, self).save()
		for group in self.plan.plan.subuser_groups.all():
			user.groups.add(group)
		
		plan_subuser_added.send(
			type(self.plan),
			plan = self.plan, user = user
		)
		
		self.plan.subusers.add(user)
		notify('bambu.saas.subuser_registered', self.plan.user,
			user = user
		)
		
		return authenticate(
			username = self.cleaned_data['username'],
			password = self.cleaned_data['password1']
		)