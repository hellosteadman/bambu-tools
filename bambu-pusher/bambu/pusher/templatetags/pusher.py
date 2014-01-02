from django.template import Library
from django.conf import settings
from bambu.pusher import KEY

register = Library()

@register.inclusion_tag('pusher/script.inc.html')
def pusher():
	return {
		'DEBUG': getattr(settings, 'DEBUG', False),
		'KEY': KEY
	}