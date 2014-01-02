# encoding: utf-8

from django.db import models
from django.db.models.signals import pre_delete
from django.contrib.contenttypes import generic
from django.conf import settings
from django.utils.timezone import get_current_timezone
from bambu.payments import states, gateways, signals, receivers
from bambu.mail import render_to_mail
from datetime import datetime, timedelta

class TaxRate(models.Model):
	name = models.CharField(max_length = 50, db_index = True)
	shorthand = models.CharField(max_length = 10, default = 'Tax', db_index = True)
	chargeable_percent = models.FloatField(u'chargeable %', db_index = True)
	payable_percent = models.FloatField(u'payable %', db_index = True)
	
	def calculate_amount(self, value):
		return round(float(value) / 100.0 * float(self.chargeable_percent), 2)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('chargeable_percent',)

class Payment(models.Model):
	content_type = models.ForeignKey('contenttypes.ContentType', editable = False)
	object_id = models.PositiveIntegerField(editable = False, db_index = True)
	content_object = generic.GenericForeignKey()
	customer = models.ForeignKey('auth.User', related_name = 'payments')
	created = models.DateTimeField(auto_now_add = True, db_index = True)
	recurring = models.PositiveIntegerField(
		choices = (
			(0, u'Never'),
			(1, u'One month'),
			(12, u'One year')
		), default = 0
	)
	
	trial_months = models.PositiveIntegerField(default = 0)
	gateway = models.CharField(max_length = 255, editable = False)
	currency = models.CharField(max_length = 3)
	net_amount = models.FloatField()
	tax_amount = models.FloatField()
	tax_rate = models.ForeignKey(TaxRate, related_name = 'payments')
	offer_net_amount = models.FloatField(default = 0)
	offer_tax_amount = models.FloatField(default = 0)
	offer_months = models.PositiveIntegerField(default = 0)
	offer_description = models.CharField(max_length = 50, null = True, blank = True)
	city = models.CharField(max_length = 100, null = True, blank = True)
	province = models.CharField(max_length = 100, null = True, blank = True)
	country = models.ForeignKey('international.Country', default = settings.COUNTRY_ID, related_name = 'payments')
	postage = models.FloatField(default = 0)
	remote_id = models.CharField(u'remote ID', max_length = 100, null = True, blank = True, db_index = True)
	
	def __unicode__(self):
		return self.remote_id or unicode(self.customer)
	
	@property
	def total_amount(self):
		return round(
			float(self.net_amount) + float(self.postage) + float(self.tax_amount), 2
		)
	
	def next(self, plus_months = 0):
		day = self.created.day
		month = self.created.month + plus_months
		year = self.created.year
		
		while month > 12:
			year += 1
			month -= 12
		
		return datetime(year, month, day, 0, 0, 0) - timedelta(days = 1).replace(tzinfo = get_current_timezone())
	
	def process_view(self, request, cancel = False, update = None):
		from bambu.payments import site
		from django.template.response import TemplateResponse
		
		try:
			latest_status = self.statuses.latest()
			state = latest_status.state
		except Status.DoesNotExist:
			state = states.PAYMENT_CREATING
		
		gateway = site.get_gateway(self.gateway)
		kwargs = {}
		
		for key, value in request.GET.items():
			kwargs[key] = value
		
		if cancel:
			return gateway.cancel_view(request, self, **kwargs)
		
		if update:
			return gateway.update_view(request, old_payment = self, new_payment = update, **kwargs)
		
		try:
			if state == states.PAYMENT_CREATING:
				return gateway.create_view(request, self)
			elif state == states.PAYMENT_AUTHORISING:
				return gateway.authorise_view(request, self, **kwargs)
			elif state == states.PAYMENT_COMPLETE:
				return TemplateResponse(
					request,
					'payments/complete.html',
					{
						'payment': self,
						'gateway': gateway
					}
				)
			elif state == states.PAYMENT_ERROR:
				return TemplateResponse(
					request,
					'payments/error.html',
					{
						'payment': self,
						'gateway': gateway
					}
				)
		except gateways.GatewayException, ex:
			self.statuses.create(
				state = states.PAYMENT_ERROR,
				label = ex.args[0]
			)
			
			return TemplateResponse(
				request,
				'payments/error.html',
				{
					'exception': ex.args,
					'gateway': gateway,
					'DEBUG': getattr(settings, 'DEBUG', False)
				}
			)
	
	class Meta:
		ordering = ('-created',)
		get_latest_by = 'created'
	
class Status(models.Model):
	payment = models.ForeignKey(Payment, related_name = 'statuses')
	changed = models.DateTimeField(auto_now_add = True, db_index = True)
	state = models.IntegerField(db_index = True,
		choices = (
			(states.PAYMENT_ERROR, u'Error'),
			(states.PAYMENT_FAILED, u'Failed'),
			(states.PAYMENT_CANCELLED, u'Cancelled'),
			(states.PAYMENT_CREATING, u'Creating'),
			(states.PAYMENT_PROCESSING, u'Processing'),
			(states.PAYMENT_AUTHORISING, u'Authorising'),
			(states.PAYMENT_COMPLETE, u'Complete'),
			(states.PAYMENT_REFUNDED, u'Refunded'),
			(states.PAYMENT_TERMINATED, u'Terminated')
		)
	)
	
	label = models.CharField(max_length = 255)
	description = models.TextField(null = True, blank = True)
	
	def __unicode__(self):
		return self.get_state_display()
	
	def save(self, *args, **kwargs):
		new = not self.pk
		super(Status, self).save(*args, **kwargs)
		
		def get_currency_symbol(currency):
			d = {}
			for (x, y, z) in getattr(settings, 'CURRENCIES', ()):
				d[x] = z
			
			return d.get(currency, u'£')
		
		if new:
			if self.state in (states.PAYMENT_ERROR, states.PAYMENT_FAILED):
				if self.state == states.PAYMENT_FAILED:
					render_to_mail(
						u'Your %s was not successful' % (
							self.payment.recurring and 'billing agreement' or 'payment'
						),
						'payments/error.txt',
						{
							'payment': self.payment,
							'currency': get_currency_symbol(self.payment.currency)
						},
						self.payment.customer
					)
				
				signals.payment_error.send(
					type(self.payment.content_object),
					payment = self.payment
				)
			elif self.state == states.PAYMENT_CANCELLED:
				signals.payment_cancelled.send(
					type(self.payment.content_object),
					payment = self.payment
				)
			elif self.state == states.PAYMENT_COMPLETE:
				signals.payment_complete.send(
					type(self.payment.content_object),
					payment = self.payment
				)
				
				render_to_mail(
					u'Your %s was successful' % (
						self.payment.recurring and 'billing agreement' or 'payment'
					),
					'payments/receipt.txt',
					{
						'payment': self.payment,
						'currency': get_currency_symbol(self.payment.currency)
					},
					self.payment.customer
				)
			elif self.state == states.PAYMENT_TERMINATED:
				signals.payment_terminated.send(
					type(self.payment.content_object),
					payment = self.payment
				)
	
	class Meta:
		ordering = ('-changed',)
		get_latest_by = 'changed'

class RemoteClient(models.Model):
	gateway = models.CharField(max_length = 255, editable = False)
	remote_id = models.CharField(max_length = 255, db_index = True)
	client = models.ForeignKey('auth.User', related_name = 'remote_records')
	
	class Meta:
		unique_together = ('gateway', 'remote_id')

class RemoteOffer(models.Model):
	gateway = models.CharField(max_length = 255, editable = False)
	remote_id = models.CharField(max_length = 255, db_index = True)
	currency = models.CharField(max_length = 3, db_index = True)
	amount = models.FloatField()
	interval = models.CharField(max_length = 10)
	name = models.CharField(max_length = 100)
	trial = models.PositiveIntegerField(default = 0)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)
		unique_together = ('gateway', 'remote_id')

class RemoteSubscription(models.Model):
	gateway = models.CharField(max_length = 255, editable = False)
	remote_id = models.CharField(max_length = 255, db_index = True)
	client = models.ForeignKey(RemoteClient, related_name = 'subscriptions')
	payment = models.ForeignKey(Payment, related_name = 'subscriptions')
	offer = models.ForeignKey(RemoteOffer, related_name = 'subscriptions')
	live = models.BooleanField(default = False, db_index = True)
	
	class Meta:
		unique_together = ('gateway', 'remote_id')

pre_delete.connect(receivers.remote_subscription_delete, sender = RemoteSubscription)
pre_delete.connect(receivers.remote_client_delete, sender = RemoteClient)