from django.contrib.sites.models import Site
from django.template.response import TemplateResponse
from django.utils import simplejson
from django.conf import settings
from django.http import HttpResponse
from django.utils.timezone import now
from bambu.payments import gateways, states
from bambu.payments.models import RemoteClient, RemoteOffer, RemoteSubscription, Payment
from bambu.international.models import Country
from urlparse import parse_qs

URL_CLIENTS = 'https://api.paymill.com/v2/clients'
URL_CLIENT = 'https://api.paymill.com/v2/clients/%s'
URL_OFFERS = 'https://api.paymill.com/v2/offers'
URL_PAYMENTS = 'https://api.paymill.com/v2/payments'
URL_TRANSACTIONS = 'https://api.paymill.com/v2/transactions'
URL_SUBSCRIPTION = 'https://api.paymill.com/v2/subscriptions/%s'
URL_SUBSCRIPTIONS = 'https://api.paymill.com/v2/subscriptions'

class PaymillGatewayAPICall(gateways.GatewayAPICall):
	def _parse(self, stream):
		return simplejson.loads(stream)

class PaymillGateway(gateways.Gateway):
	logo = 'payments/gateways/paymill.png'
	verbose_name = 'Credit or debit card'
	
	def _description(self, payment):
		site = Site.objects.get_current()
		
		if payment.recurring == 1:
			recurring = 'Monthly '
		elif payment.recurring == 12:
			recurring = 'Annual '
		else:
			recurring = ''
		
		return '%ssubscription to %s' % (
			recurring, site.name
		)
	
	def _api(self, url):
		return PaymillGatewayAPICall(url,
			username = self.credentials['PRIVATE_KEY']
		)
	
	def _client(self, customer, gateway):
		try:
			return RemoteClient.objects.get(
				client = customer,
				gateway = gateway
			)
		except RemoteClient.DoesNotExist:
			response = self._api(
				URL_CLIENTS
			).param(
				'email', customer.email
			).param(
				'description', customer.get_full_name() or customer.username
			).POST()
			
			if response.get('error'):
				if isinstance(response['error'], dict):
					message = response['error'].get('message', u'Unknown error')
				else:
					message = u'Multiple errors'
				
				raise gateways.GatewayException(
					message,
					response['error']
				)
			elif response.get('data'):
				return RemoteClient.objects.create(
					client = customer,
					remote_id = response['data']['id'],
					gateway = gateway
				)
		
		raise gateways.GatewayException(
			u'Unexpected response', response
		)
	
	def _offer(self, amount, currency, interval, trial, name, gateway):
		try:
			return RemoteOffer.objects.get(
				amount = amount,
				currency = currency,
				interval = interval,
				trial = trial,
				gateway = gateway
			)
		except RemoteOffer.DoesNotExist:
			response = self._api(
				URL_OFFERS
			).param(
				'amount', str(int(amount * 100.0))
			).param(
				'name', name
			).param(
				'currency', currency
			).param(
				'interval', interval
			).param(
				'trial_period_days', trial
			).POST()
			
			if response.get('error'):
				if isinstance(response['error'], dict):
					message = response['error'].get('message', u'Unknown error')
				else:
					message = u'Multiple errors'
				
				raise gateways.GatewayException(
					message,
					response['error']
				)
			elif response.get('data'):
				return RemoteOffer.objects.create(
					amount = amount,
					currency = currency,
					interval = interval,
					trial = trial,
					name = name,
					gateway = gateway,
					remote_id = response['data']['id']
				)
		
		raise gateways.GatewayException(
			u'Unexpected response', response
		)
	
	def _subscription(self, client, offer, payment, gateway, new_offer = None, new_payment = None):
		try:
			if new_offer and new_payment:
				subscription = RemoteSubscription.objects.select_for_update().get(
					payment = payment,
					live = self.live
				)
				
				response = self._api(
					URL_SUBSCRIPTION % subscription.remote_id
				).param(
					'offer', new_offer.remote_id
				).PUT()
				
				subscription.offer = new_offer
				subscription.payment = new_payment
				subscription.save()
			else:
				return RemoteSubscription.objects.get(
					payment = payment,
					live = self.live
				)
		except RemoteSubscription.DoesNotExist:
			response = self._api(
				URL_SUBSCRIPTIONS
			).param(
				'client', client.remote_id
			).param(
				'offer', offer.remote_id
			).param(
				'payment', payment.remote_id
			).POST()
		
		if response.get('error'):
			if isinstance(response['error'], dict):
				message = response['error'].get('message', u'Unknown error')
			else:
				message = u'Multiple errors'
			
			raise gateways.GatewayException(
				message,
				response['error']
			)
		elif response.get('data'):
			if new_offer and new_payment:
				subscription.offer = new_offer
				subscription.remote_id = response['data']['id']
				subscription.payment = new_payment
				subscription.save()
			else:
				subscription = RemoteSubscription.objects.create(
					client = client,
					offer = offer,
					live = self.live,
					gateway = gateway,
					remote_id = response['data']['id'],
					payment = payment
				)
			
			return subscription
		
		raise gateways.GatewayException(
			u'Unexpected response', response
		)
	
	def create_view(self, request, payment):
		year = now().year
		
		if request.method == 'POST' and request.POST.get('paymill_token'):
			payment.state = request.POST.get('state')
			payment.province = request.POST.get('province')
			
			try:
				payment.country = Country.objects.get(pk = request.POST.get('country'))
			except:
				if request.POST.get('country'):
					self.logger.warn('Country %s is invalid' % request.POST.get('country'))
			
			client = self._client(
				customer = payment.customer,
				gateway = payment.gateway
			)
			
			# Make the payment
			if not payment.recurring:
				response = self._api(
					URL_TRANSACTIONS
				).param(
					'amount', str(int(payment.total_amount * 100.0))
				).param(
					'currency', payment.currency
				).param(
					'description', unicode(payment.content_object)
				).param(
					'token', request.POST['paymill_token']
				).param(
					'client', client.remote_id
				).POST()
			else:
				response = self._api(
					URL_PAYMENTS
				).param(
					'token', request.POST['paymill_token']
				).param(
					'client', client.remote_id
				).POST()
			
			if response.get('error'):
				if isinstance(response['error'], dict):
					message = response['error'].get('message', u'Unknown error')
				else:
					message = u'Multiple errors'
				
				raise gateways.GatewayException(
					message,
					response['error']
				)
			elif response.get('data'):
				payment.statuses.create(
					state = states.PAYMENT_PROCESSING
				)
				
				if payment.recurring:
					payment.remote_id = response['data']['id']
				else:
					payment.remote_id = response['data']['payment']['id']
				
				payment.save()
				
				if payment.recurring:
					if payment.recurring == 1:
						interval = 'month'
					elif payment.recurring == 12:
						interval = 'year'
					else:
						raise Exception('Invalid recursion period')
					
					offer = self._offer(
						amount = payment.total_amount,
						currency = payment.currency,
						interval = interval,
						trial = payment.trial_months * 30,
						name = unicode(payment.content_object),
						gateway = payment.gateway
					)
					
					subscription = self._subscription(
						client = client,
						offer = offer,
						payment = payment,
						gateway = payment.gateway
					)
				
				payment.statuses.create(
					state = states.PAYMENT_COMPLETE
				)
				
				return self._success(request, payment, payment.remote_id)
		
		return TemplateResponse(
			request,
			'payments/gateways/paymill/create.html',
			{
				'payment': payment,
				'PUBLIC_KEY': self.credentials['PUBLIC_KEY'],
				'months': [
					(str(i), str(i).zfill(2))
					for i in range(1, 13)
				],
				'years': [
					(str(i), str(i).zfill(4))
					for i in range(year, year + 5)
				],
				'amount': int(float(payment.total_amount) * 100.0),
				'countries': Country.objects.all(),
				'country': request.POST.get('country', getattr(settings, 'COUNTRY_ID', 0))
			}
		)
	
	def update_view(self, request, old_payment, new_payment):
		old_subscription = RemoteSubscription.objects.get(
			payment = old_payment
		)
		
		if new_payment.recurring == 1:
			interval = 'month'
		elif new_payment.recurring == 12:
			interval = 'year'
		else:
			raise Exception('Invalid recursion period')
		
		new_offer = self._offer(
			amount = new_payment.total_amount,
			currency = new_payment.currency,
			interval = interval,
			trial = new_payment.trial_months * 30,
			name = unicode(new_payment.content_object),
			gateway = new_payment.gateway
		)
		
		subscription = self._subscription(
			client = old_subscription.client,
			offer = old_subscription.offer,
			payment = old_subscription.payment,
			gateway = old_subscription.payment.gateway,
			new_offer = new_offer,
			new_payment = new_payment
		)
		
		new_payment.statuses.create(
			state = states.PAYMENT_COMPLETE
		)
		
		return self._success(request, new_payment, old_payment.remote_id)
	
	def callback_view(self, request):
		json = simplejson.loads(request.body)
		event = json.get('event')
		
		if not event:
			return HttpResponse('OK')
		
		event_type = event.get('event_type')
		if not event_type:
			return HttpResponse('OK')
		
		resource = event.get('event_resource')
		if not resource:
			return HttpResponse('OK')
		
		if event_type == 'chargeback.executed':
			self.logger.error('Chargeback event received')
		elif event_type == 'transaction.created':
			self.logger.info('Transaction created')
		elif event_type == 'transaction.succeeded':
			self.logger.info('Transaction successful')
		elif event_type == 'transaction.failed':
			self.logger.info('Transaction failed')
		elif event_type == 'subscription.created':
			self.logger.info('Subscription created')
		elif event_type == 'subscription.updated':
			self.logger.info('Subscription updated')
		elif event_type == 'subscription.deleted':
			self.logger.info('Subscription deleted')
		elif event_type == 'subscription.succeeded':
			self.logger.info('Subscription successful')
		elif event_type == 'subscription.failed':
			remote_id = resource['subscription']['payment']['id']
			
			try:
				payment = Payment.objects.get(
					remote_id = remote_id
				)
			except Payment.DoesNotExist:
				self.logger.warn('Transaction failed (could not find corresponding payment)')
				return HttpResponse('OK')
			
			payment.statuses.create(
				state = states.PAYMENT_FAILED
			)
			
			self.logger.info('Payment failed')
		elif event_type == 'refund.created':
			self.logger.info('Refund created')
		elif event_type == 'refund.succeeded':
			self.logger.info('Refund successful')
		elif event_type == 'refund.failed':
			self.logger.info('Refund failed')
		
		return HttpResponse('OK')
	
	def delete_subscription(self, remote_id):
		self._api(URL_SUBSCRIPTION % remote_id).DELETE()
	
	def delete_client(self, remote_id):
		self._api(URL_CLIENT % remote_id).DELETE()