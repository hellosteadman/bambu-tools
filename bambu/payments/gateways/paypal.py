from django.contrib.sites.models import Site
from django.utils.datastructures import SortedDict
from bambu.payments import gateways, states
from urlparse import parse_qs

SANDBOX_URL_NVP = 'https://api-3t.sandbox.paypal.com/nvp'
LIVE_URL_NVP = 'https://api-3t.paypal.com/nvp'

SANDBOX_URL_IPN = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
LIVE_URL_IPN = 'https://www.paypal.com/cgi-bin/webscr'

class PayPalGatewayAPICall(gateways.GatewayAPICall):
	def _parse(self, stream):
		resp = SortedDict()
		response = super(PayPalGatewayAPICall, self)._parse(stream)
		
		for key, value in parse_qs(response).items():
			resp[key] = value[0]
		
		return resp

class PayPalGateway(gateways.Gateway):
	logo = 'payments/gateways/paypal.png'
	verbose_name = 'PayPal'
	
	def _api(self):
		call = PayPalGatewayAPICall(self.live and LIVE_URL_NVP or SANDBOX_URL_NVP)
		
		call.param('USER', self.credentials['USERNAME'])
		call.param('PWD', self.credentials['PASSWORD'])
		call.param('SIGNATURE', self.credentials['SIGNATURE'])
		call.param('VERSION', '60.0')
		
		return call
	
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
	
	def create_view(self, request, payment):
		req = self._api()
		req.param('METHOD', 'SetExpressCheckout')
		req.param('RETURNURL', self._callback_url(payment))
		req.param('CANCELURL', self._cancel_url(payment))
		req.param('EMAIL', payment.customer.email)
		
		if payment.recurring > 0:
			i = 0
			
			if payment.offer_months > 0 and payment.offer_net_amount > 0:
				req.param('PAYMENTREQUEST_%d_AMT' % i, 0)
				req.param('PAYMENTREQUEST_%d_CURRENCYCODE' % i, payment.currency)
				req.param('L_BILLINGTYPE%d' % i, 'RecurringPayments')
				req.param('L_BILLINGAGREEMENTDESCRIPTION%d' % i, payment.offer_description)
				i += 1
			
			req.param('PAYMENTREQUEST_%d_AMT' % i, 0)
			req.param('PAYMENTREQUEST_%d_CURRENCYCODE' % i, payment.currency)
			req.param('L_BILLINGTYPE%d' % i, 'RecurringPayments')
			req.param('L_BILLINGAGREEMENTDESCRIPTION%d' % i, self._description(payment))
			
			req.param('NOSHIPPING', 1)
			req.param('REQCONFIRMSHIPPING', 0)
		else:
			req.param('PAYMENTREQUEST_0_AMT', payment.total_amount)
			req.param('PAYMENTREQUEST_0_ITEMAMT', payment.net_amount)
			req.param('PAYMENTREQUEST_0_ALLOWEDPAYMENTMETHOD', 'Sale')
			req.param('PAYMENTREQUEST_0_TAXAMT', payment.tax_amount)
		
		response = req.GET()
		if 'TOKEN' in response:
			token = response['TOKEN']
			
			domain = self.live and 'www.paypal.com' or 'www.sandbox.paypal.com'
			url = 'https://%s/cgi-bin/webscr?cmd=_express-checkout&token=%s'
			return self._authorise(request, payment, url % (domain, token))
		
		raise gateways.GatewayException(response.get('L_SHORTMESSAGE0'), response)
	
	def _recurring(self, payment, token, description, total_amount, tax_amount, trial, start, billing_cycles = None):
		req = self._api()
		req.param('METHOD', 'CreateRecurringPaymentsProfile')
		req.param('TOKEN', token)
		req.param('SUBSCRIBERNAME', payment.customer.get_full_name() or payment.customer.username)
		req.param('PROFILESTARTDATE', start.strftime('%Y-%m-%dT%H:%M:%SZ'))
		req.param('PROFILEREFERENCE', payment.pk)
		req.param('AUTOBILLOUTAMT', 'AddToNextBilling')
		req.param('DESC', description)
		req.param('AMT', total_amount)
		req.param('CURRENCYCODE', payment.currency)
		req.param('TAXAMT', tax_amount)
		req.param('INITAMT', 0)
		req.param('EMAIL', payment.customer.email)
		req.param('FIRSTNAME', payment.customer.first_name)
		req.param('LASTNAME', payment.customer.last_name)
		
		if trial and payment.trial_months > 0:
			req.param('TRIALBILLINGPERIOD', 'Month')
			req.param('TRIALBILLINGFREQUENCY', 1)
			req.param('TRIALTOTALBILLINGCYCLES', payment.trial_months)
			req.param('TRIALAMT', 0)
			
			if billing_cycles:
				req.param('TOTALBILLINGCYCLES', billing_cycles)
		
		if payment.recurring == 1:
			req.param('BILLINGPERIOD', 'Month')
			req.param('BILLINGFREQUENCY', 1)
		elif payment.recurring == 12:
			req.param('BILLINGPERIOD', 'Year')
			req.param('BILLINGFREQUENCY', 1)
		else:
			req.param('SHIPPINGAMT', payment.postage)
		
		return req
	
	def authorise_view(self, request, payment, token, **kwargs):
		if payment.offer_months > 0 and payment.offer_net_amount > 0:
			req = self._recurring(
				payment = payment,
				token = token,
				start = payment.next(payment.trial_months),
				billing_cycles = payment.offer_months,
				description = payment.offer_description,
				total_amount = payment.offer_net_amount,
				tax_amount = payment.offer_tax_amount,
				trial = True,
			)
			
			response = req.GET()
			if not response['ACK'] == 'Success':
				raise gateways.GatewayException(
					response.get('L_SHORTMESSAGE0'), response
				)
		
		req = self._recurring(
			payment = payment,
			token = token,
			start = payment.next(payment.trial_months + payment.offer_months),
			description = self._description(payment),
			total_amount = payment.total_amount,
			tax_amount = payment.tax_amount,
			trial = False
		)
		
		response = req.GET()
		if response['ACK'] == 'Success':
			return self._success(request, payment, response['PROFILEID'])
		
		raise gateways.GatewayException(response.get('L_SHORTMESSAGE0'), response)
	
	def callback_view(self, request):
		if request.method == 'POST':
			call = PayPalGatewayAPICall(self.live and LIVE_URL_IPN or SANDBOX_URL_IPN)
			call.param('cmd', '_notify-validate')
			
			for key, value in request.POST.items():
				req.param(key, value[0])
			
			response = call.POST()
		else:
			from django.http import HttpResponse
			return HttpResponse('')