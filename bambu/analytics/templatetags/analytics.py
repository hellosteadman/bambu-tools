from django.template import Library
from logging import getLogger

register = Library()
LOGGER = getLogger('bambu.analytics')

@register.simple_tag(takes_context = True)
def tracking(context):
	request = context.get('request')
	if not request:
		return u''
	
	if getattr(request, '_analytics_handler', None):
		try:
			return request._analytics_handler.render(request)
		except Exception, ex:
			LOGGER.warn('Error rendering analytics code', exc_info = True)
	
	return u''