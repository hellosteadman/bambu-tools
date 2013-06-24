from bambu.urlshortener.providers import ProviderBase
from django.conf import settings
from django.utils.http import urlencode
import requests

class BitlyProvider(ProviderBase):
	def __init__(self):
		super(BitlyProvider, self).__init__()
		self.token = getattr(settings, 'SHORTURL_TOKEN', None)
		self.domain = self.domain or 'bit.ly'
	
	def shorten(self, url):
		response = requests.get(
			'https://api-ssl.bitly.com/v3/shorten?%s' % urlencode(
				{
					'access_token': self.token,
					'longUrl': self.fix(url),
					'domain': self.domain
				}
			)
		)
		
		if callable(response.json):
			json = response.json()
		elif response.json:
			json = response.json
		else:
			raise Exception(response.content)
		
		if json['status_code'] == 200:
			return json['data']['url']
		
		raise Exception(json)
	
	def unshorten(self, url):
		path = self.parse(url).path
		if path.startswith('/'):
			path = path[1:]
		
		if path.endswith('/'):
			path = path[:-1]
		
		return self.resolve(path)
	
	def resolve(self, slug):
		try:
			return ShortURL.objects.get(slug = slug).url
		except ShortURL.DoesNotExist:
			return None