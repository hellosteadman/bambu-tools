from django.template import Library
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.datastructures import SortedDict
from os import path

register = Library()

@register.inclusion_tag('bootstrap/styles.inc.html', takes_context = True)
def bootstrap_styles(context):
	css_url = getattr(settings, 'BOOTSTRAP_CSS_URL', '')
	if css_url:
		css_url = settings.MEDIA_URL + css_url
		filename, extension = path.splitext(css_url)
		if filename.endswith('.min'):
			responsive_css_url = '%s-responsive.min%s' % (filename[:-4], extension)
		else:
			responsive_css_url = '%s-responsive%s' % (filename, extension)
	else:
		responsive_css_url = ''
	
	return {
		'responsive': getattr(settings, 'BOOTSTRAP_RESPONSIVE', True),
		'css_url': css_url,
		'responsive_css_url': responsive_css_url,
		'STATIC_URL': context.get('STATIC_URL')
	}

@register.simple_tag(takes_context = True)
def bootstrap_title(context, separator = ' | '):
	title_parts = context.get('title_parts')
	site = Site.objects.get_current()
	
	if title_parts:
		return separator.join(title_parts) + separator + site.name
	else:
		return site.name

@register.inclusion_tag('bootstrap/breadcrumb.inc.html', takes_context = True)
def breadcrumb_trail(context):
	return {
		'breadcrumb_trail': context.get('breadcrumb_trail')
	}

@register.simple_tag(takes_context = True)
def html_attrs(context):
	tags = [
		('lang', 'en'),
		('class', 'no-js')
	]
	
	return ' '.join(
		['%s="%s"' % t for t in tags]
	)

@register.inclusion_tag('bootstrap/jquery-ui.inc.html', takes_context = True)
def jquery_ui(context):
	return {
		'STATIC_URL': context.get('STATIC_URL')
	}