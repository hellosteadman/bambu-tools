from django.template import Library
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from hashlib import md5

register = Library()

@register.filter()
def contenttype(value):
	return ContentType.objects.get_for_model(value).pk

@register.filter()
def gravatar(value, size = 60):
	if isinstance(value, User):
		value = value.email
	
	return mark_safe(
		'http://www.gravatar.com/avatar/%s.jpg?d=identicon&s=%d' % (
			md5(value.lower()).hexdigest(), int(size)
		)
	)