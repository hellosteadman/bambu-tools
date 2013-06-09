from django.template import Library

register = Library()

@register.simple_tag(takes_context = True)
def enqueued_scripts(context):
	return ''.join(
		[
			unicode(b) for b in context.get('enqueued_scripts', None) or [] if b
		]
	)

@register.simple_tag(takes_context = True)
def enqueued_styles(context):
	return ''.join(
		[
			unicode(b) for b in context.get('enqueued_styles', None) or [] if b
		]
	)