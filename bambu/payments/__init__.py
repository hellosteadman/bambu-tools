from django.conf import settings

class PaymentSite(object):
	_gateways = {}
	
	def get_gateway(self, klass):
		return self._gateways[klass]

site = PaymentSite()

def get_gateway_choices(with_logos = False, with_names = True):
	choices = []
	for (key, gateway) in site._gateways.items():
		choice = [key]
		
		if with_logos:
			choice.append(settings.STATIC_URL + gateway.logo)
		
		choice.append(with_names and gateway.verbose_name or u'')
		choices.append(tuple(choice))
	
	return tuple(choices)