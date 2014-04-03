from django.template import Library, TemplateSyntaxError
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from bambu.ajax import site

register = Library()

@register.simple_tag()
def ajaxurl(name, **kwargs):
    if not name in site._registry:
        raise TemplateSyntaxError(u'AJAX view %s not found' % name)

    return u'%s?%s' % (
        reverse('ajax_endpoint'),
        urlencode(
            dict(
                f = name,
                **kwargs
            )
        )
    )
