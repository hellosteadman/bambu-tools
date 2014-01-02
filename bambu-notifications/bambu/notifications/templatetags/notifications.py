from django.template import Library

register = Library()

@register.inclusion_tag('notifications/badge.inc.html', takes_context = True)
def notifications(context):
	request = context.get('request')
	if request is None:
		return
	
	user = getattr(request, 'user')
	if user is None or user.is_anonymous():
		return
	
	return {
		'notifications': request.user.notifications.all()
	}