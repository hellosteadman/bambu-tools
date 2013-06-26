from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.utils.http import urlencode
from bambu.saas.models import *
from bambu.saas.grids import SubuserGrid, InvitationGrid
from bambu.saas.decorators import feature_required
from bambu.saas.helpers import get_currency_symbol, format_price, fix_discount_code, feature_usage, feature_has_arguments
from bambu.saas.forms import *
from bambu.saas.signals import plan_signup, newsletter_optin
from bambu.payments.models import TaxRate, Payment

def _plan_features(plan):
	features = []
	for feature in Feature.objects.all():
		try:
			value = plan.plan.features.get(feature = feature).value
		except Feature.DoesNotExist:
			value = feature.is_boolean and False or 0
		
		usage = None
		usage_percent = None
		
		if not feature.is_boolean:
			if not feature_has_arguments(feature):
				usage = feature_usage(feature, plan.user)
				if value > 0:
					usage_percent = float(usage) / float(value) * 100.0
				else:
					usage_percent = 0
				
				if isinstance(usage, float):
					usage = round(usage, 1)
		
		features.append(
			{
				'name': feature.name,
				'value': value,
				'boolean': feature.is_boolean,
				'usage': usage,
				'usage_percent': usage_percent
			}
		)
	
	return features

def plans(request):
	return TemplateResponse(
		request,
		'saas/plans.html',
		{
			'matrix': Plan.objects.matrix(),
			'menu_selection': 'plans'
		}
	)

def _get_plan_prices(current_plan = None):
	currency = getattr(settings, 'DEFAULT_CURRENCY', 'GBP')
	symbol = get_currency_symbol(currency)
	
	tax_rate = TaxRate.objects.get(
		chargeable_percent = settings.PAYMENTS_DEFAULT_TAXRATE
	)
	
	plans = Plan.objects.all()
	if current_plan:
		plans = plans.exclude(
			pk = current_plan.pk
		).filter(
			order__gte = current_plan.order
		)
	
	prices = {}
	for p in plans:
		try:
			price = p.prices.get(currency = currency)
			price_monthly = format_price(symbol, price.monthly)
			price_yearly = format_price(symbol, price.yearly)
		except Price.DoesNotExist:
			price_monthly = format_price(symbol, 0)
			price_yearly = format_price(symbol, 0)

		prices[p.pk] = (
			(1, _(u'Monthly (%s + %s)' % (price_monthly, tax_rate.shorthand)), price.monthly),
			(12, _(u'Annually (%s + %s)' % (price_yearly, tax_rate.shorthand)), price.yearly)
		)
	
	return prices

@login_required
def upgrade(request):
	feature = request.GET.get('feature')
	form = None
	plan = request.plan()
	
	if not plan:
		raise Http404('UserPlan not found.')
	
	if plan.user.pk == request.user.pk:
		form = PlanChangeForm(request.POST or None, current_plan = plan)
	
	value = None
	
	if feature:
		try:
			feature = plan.plan.features.get(feature__slug = feature)
			value = feature.value
		except PlanFeature.DoesNotExist:
			feature = None
	
	if request.method == 'POST' and form and form.is_valid():
		with transaction.commit_on_success():
			change = form.save()
			
			if change.paid:
				messages.success(request, u'Your account has been updated successfully.')
				return HttpResponseRedirect(
					settings.LOGIN_REDIRECT
				)
			else:
				request.session['PAYMENT_GATEWAY'] = form.cleaned_data.get('payment_gateway')
				
				return HttpResponseRedirect(
					reverse('upgrade_pay')
				)
	
	prices = _get_plan_prices(plan.plan)
	return TemplateResponse(
		request,
		'saas/upgrade.html',
		{
			'feature': feature,
			'value': value,
			'plan': plan.plan,
			'form': form,
			'menu_selection': 'profile',
			'plan_prices': simplejson.dumps(prices),
			'matrix': Plan.objects.exclude(
				pk = plan.plan.pk
			).filter(
				order__gte = plan.plan.order
			).matrix
		}
	)

@login_required
def upgrade_pay(request):
	plan = request.plan()
	if not plan:
		raise Http404('UserPlan not found.')
	
	if plan.user.pk != request.user.pk:
		messages.warning(request, u'You can\'t make changes to another user\'s account.')
		return HttpResponseRedirect(
			settings.LOGIN_REDIRECT
		)
	
	currency = getattr(settings, 'DEFAULT_CURRENCY', 'GBP')
	
	try:
		change = UserPlanChange.objects.get(user = request.user, paid = False)
	except UserPlanChange.MultipleObjectsReturned:
		change = UserPlanChange.objects.filter(user = request.user, paid = False).latest()
	except UserPlanChange.DoesNotExist:
		messages.warning(request, u'You don\'t have any account changes to pay for.')
		
		return HttpResponseRedirect(
			reverse('upgrade')
		)
	
	try:
		payment = change.get_payment()
		gateway = payment.gateway
		
		if payment.remote_id:
			return payment.process_view(request,
				update = change.create_payment(currency, gateway)
			)
		else:
			return payment.process_view(request)
	except Payment.DoesNotExist:
		try:
			payment = plan.get_payment()
			gateway = payment.gateway
		except Payment.DoesNotExist:
			gateway = request.session.get('PAYMENT_GATEWAY')
			payment = None
		
		if not gateway:
			return HttpResponse('No payment gateway provided.')
		
		if payment:
			return payment.process_view(request,
				update = change.create_payment(currency, gateway)
			)
		else:
			return change.create_payment(
				currency, gateway
			).process_view(request)

def signup(request):
	if request.user.is_authenticated():
		messages.warning(request, u'You already have an account.')
		
		return HttpResponseRedirect(
			getattr(settings, 'LOGIN_REDIRECT_URL', '/')
		)
		
	plan = get_object_or_404(Plan,
		pk = request.GET.get('plan') or settings.SAAS_DEFAULT_PLAN
	)
	
	if request.GET.get('discount'):
		code = fix_discount_code(request.GET.get('discount', ''))
		if not code and request.method == 'GET':
			messages.warning(request, '%s is not a valid discount code' % request.GET['discount'])
	else:
		code = ''
	
	form = SignupForm(
		data = request.POST or None,
		challenge_words = request.session.get('challenge_words'),
		initial = {
			'plan': plan.pk,
			'discount_code': code
		}
	)
	
	if request.method == 'POST':
		with transaction.commit_on_success():
			if form.is_valid():
				if 'challenge_words' in request.session:
					del request.session['challenge_words']
					request.session.modified = True
			
				user = form.save()
				plan = form.cleaned_data.get('plan',
					Plan.objects.get(pk = settings.SAAS_DEFAULT_PLAN),
				)
			
				if 'bambu.analytics' in settings.INSTALLED_APPS:
					from bambu.analytics import track_event, events
					track_event(request, events.EVENT,
						category = u'Users',
						action = u'Signup',
						option_label = plan.name,
						option_value = user.pk
					)
			
				if form.cleaned_data.get('newsletter_optin'):
					user.pending_newsletter_optins.create()
			
				currency = getattr(settings, 'DEFAULT_CURRENCY', 'GBP')
				price = plan.prices.get(currency = currency)
			
				if price.monthly == 0:
					user.email_validations.create()
					for group in plan.groups.all():
						user.groups.add(group)
				
					return HttpResponseRedirect(
						reverse('signup_complete')
					)
				else:
					login(request, user)
					request.session['PAYMENT_GATEWAY'] = form.cleaned_data['payment_gateway']
				
					return HttpResponseRedirect(
						reverse('signup_pay')
					)
	else:
		request.session['challenge_words'] = form.challenge_words
		request.session.modified = True
	
	prices = _get_plan_prices()
	return TemplateResponse(
		request,
		'saas/signup.html',
		{
			'form': form,
			'selected_plan': plan,
			'next': request.GET.get('next'),
			'matrix': Plan.objects.matrix,
			'plan_prices': simplejson.dumps(prices),
			'discount': code
		}
	)

@never_cache
@login_required(login_url = '/signup/')
def signup_pay(request):
	try:
		plan = UserPlan.objects.get(user = request.user, paid = False)
	except UserPlan.DoesNotExist:
		messages.warning(request, u'You already have an account.')
		
		return HttpResponseRedirect(
			getattr(settings, 'LOGIN_REDIRECT_URL', '/')
		)
	
	gateway = request.session.get('PAYMENT_GATEWAY')
	if not gateway:
		return HttpResponse('No payment gateway provided.')
	
	currency = getattr(settings, 'DEFAULT_CURRENCY', 'GBP')
	
	try:
		payment = plan.get_payment()
	except Payment.DoesNotExist:
		payment = plan.create_payment(currency, gateway)
	
	response = payment.process_view(request)
	if response is None:
		return HttpResponseRedirect('../')
	
	return response

@never_cache
def verify_email(request, guid = None):
	if guid:
		with transaction.commit_on_success():
			validation = get_object_or_404(EmailValidation, guid = guid)
			
			user = validation.user
			user.is_active = True
			user.save()
			
			if user.pending_newsletter_optins.exists():
				newsletter_optin.send(
					type(user),
					user = user
				)
				
				user.pending_newsletter_optins.all().delete()
			
			validation.delete()
			messages.success(request, _('Thanks for confirming your email address.'))
			
			plan_signup.send(
				UserPlan,
				plan = UserPlan.objects.get_for_user(user),
				user = user
			)
			
			next = getattr(settings, 'SIGNUP_REDIRECT',
				getattr(settings, 'LOGIN_REDIRECT_URL', '/')
			)
			
			return HttpResponseRedirect(
				'%s?%s' % (
					settings.LOGIN_URL,
					urlencode(
						{
							'next': next
						}
					)
				)
			)
	
	return TemplateResponse(
		request,
		'saas/signup-complete.html',
		{}
	)

@never_cache
def reset_password(request, guid = None):
	if guid:
		with transaction.commit_on_success():
			reset = get_object_or_404(PasswordReset, guid = guid)
			reset.reset()
			
			messages.success(request,
				_('Your new password should be in your inbox shortly.')
			)
			
			return HttpResponseRedirect(settings.LOGIN_URL)
	
	form = PasswordResetForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		with transaction.commit_on_success():
			try:
				user = User.objects.get(email__iexact = form.cleaned_data['email'])
				reset, created = user.password_resets.get_or_create()
			except User.DoesNotExist:
				pass
			
			return TemplateResponse(
				request,
				'saas/password-reset.html'
			)
	
	return TemplateResponse(
		request,
		'saas/forgot-password.html',
		{
			'form': form
		}
	)

@never_cache
@login_required
def profile(request):
	plan = request.plan()
	higher_plans = 	Plan.objects.exclude(
		pk = plan.plan.pk
	).filter(
		order__gte = plan.plan.order
	)
	
	return TemplateResponse(
		request,
		'saas/profile/dashboard.html',
		{
			'plan': plan,
			'plan_features': _plan_features(plan),
			'breadcrumb_trail': (
				('../', u'Home'),
				('', u'My profile')
			),
			'menu_selection': 'profile',
			'title_parts': ('My profile',),
			'matrix': higher_plans.matrix,
			'can_upgrade': higher_plans.exists()
		}
	)

@never_cache
@login_required
def profile_edit(request):
	form = ProfileForm(
		data = request.POST or None,
		instance = request.user
	)
	
	if request.method == 'POST' and form.is_valid():
		with transaction.commit_on_success():
			user = form.save()
			messages.success(request, u'Your profile has been updated.')
		
			return HttpResponseRedirect(
				reverse('profile')
			)
	
	return TemplateResponse(
		request,
		'saas/profile/edit.html',
		{
			'form': form,
			'breadcrumb_trail': (
				('../../', u'Home'),
				('../', u'My profile'),
				('', 'Edit')
			),
			'menu_selection': 'profile:edit',
			'title_parts': ('Edit', 'My profile')
		}
	)

@never_cache
@login_required
@permission_required('saas.change_subuser')
def profile_subusers(request):
	plan = request.plan()
	
	return TemplateResponse(
		request,
		'saas/profile/subusers.html',
		{
			'form': InvitationsForm(plan = plan, user = request.user),
			'grid': SubuserGrid(request, plan.subusers.all(), prefix = 'subusers'),
			'breadcrumb_trail': (
				('../../', u'Home'),
				('../', u'My profile'),
				('', 'Teammates')
			),
			'menu_selection': 'profile:subusers',
			'title_parts': ('Teammates', 'My profile')
		}
	)

@never_cache
@login_required
@permission_required('saas.change_subuser')
def profile_subusers_invitations(request):
	plan = request.plan()
	
	return TemplateResponse(
		request,
		'saas/profile/invitations.html',
		{
			'grid': InvitationGrid(request, plan.invitations.all(), prefix = 'invitations'),
			'breadcrumb_trail': (
				('../../../', u'Home'),
				('../../', u'My profile'),
				('../', u'Teammates'),
				('', u'Invitations')
			),
			'menu_selection': 'profile:subusers:invitations',
			'title_parts': ('Invitations', 'Teammates', 'My profile')
		}
	)

@never_cache
@feature_required('subusers')
@permission_required('saas.create_subuser')
def profile_subusers_invite(request):
	plan = request.plan()
	form = InvitationsForm(request.POST or None, plan = plan, user = request.user)
	
	if request.method == 'POST' and form.is_valid():
		with transaction.commit_on_success():
			invitations = form.save()
			if len(invitations) > 0:
				messages.success(request, u'Your invitations have been sent successfully.')
			
			if request.is_ajax():
				return HttpResponse('::OK::')
			else:
				return HttpResponseRedirect(
					reverse('profile_subusers')
				)
	
	if request.is_ajax():
		return TemplateResponse(
			request,
			'form.inc.html',
			{
				'form': form
			}
		)
	
	return TemplateResponse(
		request,
		'saas/profile/subusers.html',
		{
			'form': form,
			'breadcrumb_trail': (
				('../../', u'Home'),
				('../', u'My profile'),
				('', 'Teammates')
			),
			'menu_selection': 'profile:subusers',
			'title_parts': ('Teammates', 'My profile')
		}
	)

@never_cache
def invitation_accept(request, guid):
	if request.user.is_authenticated():
		messages.warning(request, u'You already have an account.')
		
		return HttpResponseRedirect(
			getattr(settings, 'LOGIN_REDIRECT_URL', '/')
		)
	
	invitation = get_object_or_404(Invitation, guid = guid)
	form = AcceptInvitationForm(request.POST or None,
		plan = invitation.plan,
		initial = {
			'email': invitation.email
		}
	)
	
	if request.method == 'POST' and form.is_valid():
		with transaction.commit_on_success():
			user = form.save()
			invitation.delete()
			login(request, user)
			
			return HttpResponseRedirect(
				getattr(settings, 'LOGIN_REDIRECT_URL', '/')
			)
	
	return TemplateResponse(
		request,
		'saas/invitation.html',
		{
			'form': form,
			'next': request.GET.get('next'),
			'invitation': invitation,
			'plan': invitation.plan,
			'plan_features': _plan_features(invitation.plan)
		}
	)

@never_cache
@login_required
@permission_required('saas.delete_subuser')
def profile_delete_subuser(request, username):
	plan = request.plan()
	
	try:
		user = plan.subusers.exclude(pk = request.user.pk).get(username = username)
	except User.DoesNotExist:
		raise Http404('User not found.')
	
	if request.method == 'POST':
		plan.subusers.remove(user)
		
		messages.success(
			request,
			u'The user has been removed from your team.'
		)
		
		return HttpResponseRedirect('../../')
	
	return TemplateResponse(
		request,
		'saas/profile/delete-subuser' + (
			request.is_ajax() and '.inc.html' or '.html'
		),
		{
			'deluser': user,
			'next': '../../',
			'breadcrumb_trail': (
				('../../../', u'Home'),
				('../../', u'My profile'),
				('../', 'Teammates'),
				('', u'Remove')
			),
			'title_parts': (u'Remove', 'Teammates', 'My profile')
		}
	)

@never_cache
@login_required
@permission_required('saas.change_subuser')
@transaction.commit_on_success
def profile_delete_invitation(request, guid):
	plan = request.plan()
	get_object_or_404(Invitation, plan = plan, guid = guid).delete()
	
	messages.success(
		request,
		u'The invitation has been cancelled.'
	)
	
	return HttpResponseRedirect('../../')

@never_cache
@login_required
@permission_required('saas.change_subuser')
def profile_resend_invitation(request, guid):
	plan = request.plan()
	get_object_or_404(Invitation, plan = plan, guid = guid).send()
	
	messages.success(
		request,
		u'The invitation has been resent.'
	)

	return HttpResponseRedirect('../../')