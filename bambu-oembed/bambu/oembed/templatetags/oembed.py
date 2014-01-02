from django.template import Library
from django.conf import settings
from django.utils.safestring import mark_safe
from bambu.oembed import URL_REGEX, URL_PATTERNS
from bambu.oembed.models import Resource
import re

PATTERNS = list(URL_PATTERNS) + getattr(settings, 'OEMBED_URL_PATTERNS', [])
WIDTH = getattr(settings, 'OEMBED_WIDTH', 640)

register = Library()

@register.filter()
def oembed(value, width = WIDTH):
	if not '<p' in value and not '</p>' in value:
		value = '<p>%s</p>' % value
	
	match = URL_REGEX.search(value)
	if match is None:
		match = URL_REGEX.search(value)
	
	while not match is None and match.end() <= len(value):
		start = match.start()
		end = match.end()
		groups = match.groups()
		
		if len(groups) > 0:
			url = groups[0]
			inner = '<p><a href="%(url)s">%(url)s</a></p>' % {
				'url': url
			}
			
			for (pattern, endpoint, format) in PATTERNS:
				if not re.match(pattern, url, re.IGNORECASE) is None:
					try:
						resource = Resource.objects.get(
							url = url,
							width = width
						)
					except Resource.DoesNotExist:
						try:
							resource = Resource.objects.create_resource(
								url, width, endpoint, format
							)
						except:
							break
					
					inner = resource.html
					break
		else:
			inner = ''
		
		value = value[:start] + inner + value[end:]
		match = URL_REGEX.search(value, start + len(inner))
	
	return mark_safe(value)