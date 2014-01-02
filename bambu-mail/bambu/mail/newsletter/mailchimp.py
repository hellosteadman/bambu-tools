from bambu.mail.newsletter import ProviderBase
from django.conf import settings
from xmlrpclib import ServerProxy

API_URL = 'http://%s.api.mailchimp.com/1.3/'

class MailChimpProvider(ProviderBase):
	def subscribe(self, email, list_id, **kwargs):
		key, dash, dc = self.settings.get('API_KEY', '').rpartition('-')
		if not key or not dc:
			raise Exception('Missing or invalid API key')
		
		url = API_URL % dc
		proxy = ServerProxy(url, allow_none = True)
		
		proxy.listSubscribe(
			key,
			self.settings.get('LIST_IDS', {}).get(list_id, None),
			email,
			*self.map_args('subscribe', **kwargs)
		)