from django.db import models
from django.conf import settings
from django.utils.datastructures import SortedDict
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.timezone import get_current_timezone, now as rightnow
from django.utils import simplejson
from bambu.saas import helpers, receivers
from bambu.saas.managers import PlanManager, UserPlanManager
from bambu.mail.shortcuts import render_to_mail
from bambu.payments.models import Payment, TaxRate
from bambu.payments import signals as payment
from datetime import datetime, timedelta
from uuid import uuid4
import logging

class Plan(models.Model):
	name = models.CharField(max_length = 50)
	description = models.TextField(null = True, blank = True)
	best_value = models.BooleanField(default = False)
	order = models.PositiveIntegerField(default = 1, db_index = True)
	trial_months = models.PositiveIntegerField('trial period', default = 0,
		help_text = u'Number of months worth of free trial'
	)
	
	groups = models.ManyToManyField('auth.Group', related_name = 'groups',
		null = True, blank = True,
		help_text = u'Select the groups that provide permissions to this user'
	)
	
	subuser_groups = models.ManyToManyField('auth.Group', related_name = 'subuser_groups',
		null = True, blank = True,
		help_text = u'Select the groups that provide permissions to this user\'s teammates'
	)
	
	objects = PlanManager()
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('order',)
	
	class QuerySet(models.query.QuerySet):
		def with_prices(self, currency):
			return self.extra(
				select = {
					'price_monthly': 'SELECT `saas_price`.`monthly` FROM `saas_price` WHERE ' \
						'`saas_price`.`plan_id` = `saas_plan`.`id` AND ' \
						'`saas_price`.`currency` = %s LIMIT 1',
					'price_yearly': 'SELECT `saas_price`.`yearly` FROM `saas_price` WHERE ' \
						'`saas_price`.`plan_id` = `saas_plan`.`id` AND ' \
						'`saas_price`.`currency` = %s LIMIT 1'
				},
				select_params = (currency, currency)
			)
		
		def matrix(self, currency = None):
			headings = []
			features = SortedDict()
			currency = currency or getattr(settings, 'CURRENCY_CODE', 'GBP')
			
			for feature in Feature.objects.select_related().extra(
				select = {
					'values': 'SELECT CONCAT(\'{\', GROUP_CONCAT(CONCAT(\'"\', `plan_id`, \'":"\', `value`, \'"\')), \'}\') FROM `saas_planfeature` WHERE ' \
						'`saas_planfeature`.`feature_id` = `saas_feature`.`id`'
				}
			):
				features[feature.slug] = (
					feature.name,
					feature.is_boolean,
					feature.description,
					feature.values
				)
			
			rows = [
				{
					'heading': n,
					'columns': c,
					'slug': k,
					'boolean': b,
					'description': d or u''
				} for (k, (n, b, d, c)) in features.items()
			]
			
			symbol = helpers.get_currency_symbol(currency)
			plans = self.with_prices(currency)
			for plan in plans:
				h = {
					'name': plan.name,
					'pk': plan.pk
				}
				
				if plan.best_value:
					h['best'] = True
				
				if plan.price_monthly or plan.price_yearly:
					h.update(
						{
							'price_monthly': helpers.format_price(
								symbol, plan.price_monthly
							) or None,
							'price_yearly': helpers.format_price(
								symbol, plan.price_yearly
							) or None
						}
					)
				
				headings.append(h)
			
			for row in rows:
				columns = []
				column_dict = row['columns']
				
				if column_dict:
					column_dict = simplejson.loads(row['columns'])
				else:
					column_dict = {}
				
				for plan in plans:
					column_item = column_dict.get(unicode(plan.pk), -1)
					columns.append(
						{
							'value': column_item,
							'best': plan.best_value
						}
					)
				
				row['columns'] = columns
			
			return {
				'headings': headings,
				'rows': rows
			}
	
class Price(models.Model):
	plan = models.ForeignKey(Plan, related_name = 'prices')
	monthly = models.DecimalField(decimal_places = 2, max_digits = 6, db_index = True)
	yearly = models.DecimalField(decimal_places = 2, max_digits = 8, db_index = True)
	currency = models.CharField(max_length = 3, choices = helpers.get_currencies(),
		default = getattr(settings, 'CURRENCY_CODE', 'GBP'), db_index = True
	)
	
	def get_currency_symbol(self):
		return helpers.get_currency_symbol(self.currency)
	
	def __unicode__(self):
		return u'%s%s per month' % (self.get_currency_symbol(), self.monthly)
	
	class Meta:
		ordering = ('monthly',)
		unique_together = ('plan', 'currency')

class Feature(models.Model):
	name = models.CharField(max_length = 50)
	slug = models.SlugField(max_length = 50, unique = True)
	is_boolean = models.BooleanField(default = False)
	order = models.PositiveIntegerField(default = 1, db_index = True)
	description = models.TextField(null = True, blank = True)
	test_function = models.CharField(max_length = 255, null = True, blank = True)
	upgrade_cta = models.CharField(u'upgrade call-to-action',
		max_length = 255, null = True, blank = True
	)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('order',)

class PlanFeature(models.Model):
	plan = models.ForeignKey(Plan, related_name = 'features')
	feature = models.ForeignKey(Feature, related_name = 'plans', db_index = True)
	value = models.IntegerField(default = 0, help_text = u'Use -1 for unlimited', db_index = True)
	
	def __unicode__(self):
		return u'%s (%s)' % (
			self.feature,
			self.feature.is_boolean and (self.value == 1 and 'Yes' or 'No') or self.value
		)
	
	class Meta:
		unique_together = ('plan', 'feature')

class Discount(models.Model):
	name = models.CharField(max_length = 50)
	description = models.TextField(null = True, blank = True)
	percent = models.FloatField()
	months = models.PositiveIntegerField(
		default = 1, db_index = True,
		help_text = u'The number of months the discount applies for'
	)
	
	code = models.CharField(max_length = 50, unique = True, db_index = True)
	valid_yearly = models.BooleanField(default = True)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('-percent',)

class UserPlan(models.Model):
	plan = models.ForeignKey(Plan, related_name = 'users')
	user = models.ForeignKey(User, related_name = 'plans', unique = True)
	subusers = models.ManyToManyField(User, related_name = 'parent_plans', blank = True)
	started = models.DateField(db_index = True)
	paid_start = models.DateField()
	expiry = models.DateField(null = True, blank = True)
	renewed = models.DateField(null = True, blank = True)
	period = models.PositiveIntegerField(db_index = True,
		choices = (
			(1, u'One month'),
			(12, u'One year')
		), default = 12
	)
	
	paid = models.BooleanField(default = False)
	discount = models.ForeignKey('saas.Discount', related_name = 'user_plans',
		null = True, blank = True
	)
	
	objects = UserPlanManager()
	
	def __unicode__(self):
		return unicode(self.user.get_full_name() or self.user.username)
	
	def has_feature(self, feature, **kwargs):
		try:
			feat = self.plan.features.get(feature__slug = feature)
		except Feature.DoesNotExist:
			return False
		
		if (feat.feature.is_boolean and feat.value) or feat.value == -1:
			return True
		elif helpers.test_feature(feat.feature, self.user, feat.value, **kwargs):
			return True
		
		return False
	
	def save(self, *args, **kwargs):
		if not self.started:
			now = rightnow()
			self.started = now
			
			day = now.day
			month = now.month + self.plan.trial_months
			year = now.year
			
			while month > 12:
				year += 1
				month -= 12
			
			self.paid_start = (
				datetime(year, month, day, 0, 0, 0) - timedelta(days = 1)
			).replace(tzinfo = get_current_timezone())
			
			day = self.paid_start.day
			month = self.paid_start.month + self.period
			year = self.paid_start.year
			
			while month > 12:
				year += 1
				month -= 12
			
			self.expiry = (
				datetime(year, month, day, 0, 0, 0) - timedelta(days = 1)
			).replace(tzinfo = get_current_timezone())
		
		super(UserPlan, self).save(*args, **kwargs)
	
	def get_payment(self):
		from django.contrib.contenttypes.models import ContentType
		
		try:
			change = UserPlanChange.objects.get(
				user = self.user,
				new_plan = self.plan
			)
			
			return change.get_payment()
		except UserPlanChange.DoesNotExist:
			return Payment.objects.get(
				content_type = ContentType.objects.get_for_model(self),
				object_id = self.pk,
				customer = self.user
			)
	
	def create_payment(self, currency, gateway):
		from django.contrib.contenttypes.models import ContentType
		
		price = self.plan.prices.get(currency = currency)
		if self.period == 1:
			amount = float(price.monthly)
		else:
			amount = float(price.yearly)
		
		if self.discount:
			offer_amount = round(amount - (amount / 100.0 * self.discount.percent), 2)
			offer_months = self.discount.months
		else:
			offer_amount = 0
			offer_months = 0
		
		tax_rate = TaxRate.objects.get(
			chargeable_percent = getattr(settings, 'PAYMENTS_DEFAULT_TAXRATE')
		)
		
		if amount > 0:
			return Payment.objects.create(
				content_type = ContentType.objects.get_for_model(self),
				object_id = self.pk,
				customer = self.user,
				currency = currency,
				gateway = gateway,
				net_amount = amount,
				tax_amount = tax_rate.calculate_amount(amount),
				offer_net_amount = offer_amount,
				offer_tax_amount = tax_rate.calculate_amount(offer_amount),
				offer_months = offer_months,
				offer_description = self.discount and self.discount.name or '',
				recurring = self.period,
				trial_months = self.plan.trial_months,
				tax_rate = tax_rate
			)
		else:
			return None
	
	class Meta:
		ordering = ('-renewed', '-started')
		permissions = (
			('create_subuser', u'Can invite teammate'),
			('change_subuser', u'Can change teammate'),
			('delete_subuser', u'Can delete teammate')
		)

class UserPlanChange(models.Model):
	user = models.ForeignKey('auth.User', related_name = 'plan_changes')
	old_plan = models.ForeignKey('Plan', related_name = 'changed_from')
	new_plan = models.ForeignKey('Plan', related_name = 'changed_to')
	period = models.PositiveIntegerField(db_index = True,
		choices = (
			(1, u'One month'),
			(12, u'One year')
		), default = 12
	)
	
	changed = models.DateTimeField(auto_now_add = True, db_index = True)
	paid = models.BooleanField(default = False, db_index = True)
	discount = models.ForeignKey('saas.Discount', related_name = 'user_plan_changes',
		null = True, blank = True
	)
	
	def __unicode__(self):
		return self.new_plan.name
	
	def get_payment(self):
		from django.contrib.contenttypes.models import ContentType
		
		return Payment.objects.get(
			content_type = ContentType.objects.get_for_model(self),
			object_id = self.pk,
			customer = self.user
		)
	
	def create_payment(self, currency, gateway):
		from django.contrib.contenttypes.models import ContentType
		
		price = self.new_plan.prices.get(currency = currency)
		if self.period == 1:
			amount = float(price.monthly)
		else:
			amount = float(price.yearly)
		
		if self.discount:
			offer_amount = round(amount - (amount / 100.0 * self.discount.percent), 2)
			offer_months = self.discount.months
		else:
			offer_amount = 0
			offer_months = 0
		
		tax_rate = TaxRate.objects.get(
			chargeable_percent = getattr(settings, 'PAYMENTS_DEFAULT_TAXRATE')
		)
		
		if amount > 0:
			return Payment.objects.create(
				content_type = ContentType.objects.get_for_model(self),
				object_id = self.pk,
				customer = self.user,
				currency = currency,
				gateway = gateway,
				net_amount = amount,
				tax_amount = tax_rate.calculate_amount(amount),
				offer_net_amount = offer_amount,
				offer_tax_amount = tax_rate.calculate_amount(offer_amount),
				offer_months = offer_months,
				offer_description = self.discount and self.discount.name or '',
				recurring = self.period,
				trial_months = 0,
				tax_rate = tax_rate
			)
		else:
			return None
	
	def save(self, *args, **kwargs):
		new = not self.pk
		newly_paid = False
		
		if self.paid:
			if not new:
				old = UserPlanChange.objects.get(pk = self.pk)
				if not old.paid:
					newly_paid = True
			else:
				newly_paid = True
		
		super(UserPlanChange, self).save(*args, **kwargs)
		
		if not newly_paid:
			return
		
		for group in self.old_plan.groups.all():
			self.user.groups.remove(group)
		
		try:
			plan = UserPlan.objects.select_for_update().get(
				user = self.user,
				plan = self.old_plan
			)
			
			for user in plan.subusers.all():
				for group in plan.subuser_groups.all():
					user.groups.remove(group)
			
			plan.paid = True
			plan.plan = self.new_plan
			plan.save()
		except UserPlan.DoesNotExist:
			plan = UserPlan.objects.create(
				user = self.user,
				plan = self.new_plan,
				paid = True,
				paid_start = rightnow()
			)
		
		for group in self.new_plan.groups.all():
			self.user.groups.add(group)
		
		for user in plan.subusers.all():
			for group in plan.subuser_groups.all():
				user.groups.add(group)
	
	class Meta:
		ordering = ('-changed',)
		get_latest_by = 'changed'
		db_table = 'saas_userplan_changes'

class EmailValidation(models.Model):
	user = models.ForeignKey(User, related_name = 'email_validations', unique = True)
	guid = models.CharField(max_length = 36, unique = True)
	sent = models.DateTimeField(auto_now_add = True)
	
	def __unicode__(self):
		return self.guid
	
	def save(self, *args, **kwargs):
		if not self.guid:
			self.guid = unicode(uuid4())
		
		new = not self.pk
		super(EmailValidation, self).save(*args, **kwargs)
		
		self.user.is_active = False
		self.user.save()
		
		if new:
			render_to_mail(
				subject = u'Please confirm your email address',
				template = 'saas/mail/validate.txt',
				context = {
					'name': self.user.first_name or self.user.username,
					'guid': self.guid
				},
				recipient = self.user
			)
	
	class Meta:
		ordering = ('-sent',)
		get_latest_by = 'sent'

class PasswordReset(models.Model):
	user = models.ForeignKey(User, related_name = 'password_resets', unique = True)
	guid = models.CharField(max_length = 36, unique = True)
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
				template = 'saas/mail/password-reset.txt',
				context = {
					'name': self.user.first_name or self.user.username,
					'guid': self.guid
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
			template = 'saas/mail/password.txt',
			context = {
				'name': self.user.first_name or self.user.username,
				'username': self.user.username,
				'password': password
			},
			recipient = self.user
		)
	
	class Meta:
		ordering = ('-sent',)
		get_latest_by = 'sent'

class Invitation(models.Model):
	guid = models.CharField(max_length = 36, unique = True)
	sender = models.ForeignKey('auth.User', related_name = 'invitations_sent')
	plan = models.ForeignKey(UserPlan, related_name = 'invitations')
	email = models.EmailField(unique = True)
	
	def send(self):
		site = Site.objects.get_current()
		sender_name = self.sender.get_full_name() or self.sender.username
		
		render_to_mail(
			u'Invitation to join %s on %s' % (
				sender_name,
				site.name
			),
			'saas/mail/invitation.txt',
			{
				'sender': sender_name,
				'guid': self.guid,
				'reminder': not self.pk is None
			},
			self.email,
			fail_silently = True
		)
	
	def save(self, *args, **kwargs):
		if not self.guid:
			self.guid = unicode(uuid4())
		
		if not self.pk:
			self.send()
		
		super(Invitation, self).save(*args, **kwargs)

class NewsletterOptInPending(models.Model):
	user = models.ForeignKey(
		'auth.User',
		related_name = 'pending_newsletter_optins',
		unique = True
	)
	
	created = models.DateTimeField(auto_now_add = True)
	
	def __unicode__(self):
		return unicode(self.user)
	
	class Meta:
		db_table = 'auth_user_nloptins'

payment.payment_complete.connect(receivers.payment_complete, sender = UserPlan)
payment.payment_complete.connect(receivers.payment_complete_change, sender = UserPlanChange)
payment.payment_cancelled.connect(receivers.payment_complete_change, sender = UserPlan)
payment.payment_error.connect(receivers.payment_error, sender = UserPlan)
payment.payment_terminated.connect(receivers.payment_terminated, sender = UserPlan)