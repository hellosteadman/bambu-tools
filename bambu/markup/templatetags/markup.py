from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.conf import settings
from markdown import markdown as m

register = Library()
EXTENSIONS = getattr(settings, 'MARKDOWN_EXTENSIONS', ())
ENABLE_ATTRIBUTES = getattr(settings, 'MARKDOWN_ENABLE_ATTRIBUTES', False)

@register.filter(is_safe = True)
@stringfilter
def markdown(value):
	return mark_safe(
		m(
			force_unicode(value),
			EXTENSIONS,
			enable_attributes = ENABLE_ATTRIBUTES
		)
	)