from django.db.models import Manager
from bambu.oembed import get_oembed_content

class ResourceManager(Manager):
	def create_resource(self, url, width, endpoint, format):
		html = get_oembed_content(url, endpoint, format, width)
		
		return self.create(
			url = url,
			width = width,
			html = html
		)