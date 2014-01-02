from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

@register.simple_tag()
def icon(kind, colour = 'black'):
	classes = ['icon-%s' % kind]
	
	if colour and colour != 'black':
		classes.append('icon-%s' % colour)
	
	return mark_safe(
		u'<i class="%s"></i>' % ' '.join(classes)
	)