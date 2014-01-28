from django.template import Library
from django.conf import settings
from bambu.pusher import KEY

register = Library()

@register.inclusion_tag('pusher/script.inc.html', takes_context = True)
def pusher(context):
    request = context.get('request')
    if request is None:
        return {}
    
    return {
        'DEBUG': getattr(settings, 'DEBUG', False),
        'KEY': KEY,
        'SSL': request.is_secure(),
        'VERSION': getattr(settings, 'PUSHER_VERSION', '2.0')
    }