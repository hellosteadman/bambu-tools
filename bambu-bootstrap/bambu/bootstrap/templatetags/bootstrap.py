from django.template import Library
from django.template.base import get_library, InvalidTemplateLibrary
from django.template.defaulttags import LoadNode
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.datastructures import SortedDict
from os import path

register = Library()
SITE = Site.objects.get_current()

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
	
	responsive = getattr(settings, 'BOOTSTRAP_RESPONSIVE', True)
	if not css_url and getattr(settings, 'BOOTSTRAP_VERSION', '2.3.2').startswith('3.0'):
		css_url = settings.STATIC_URL + 'bootstrap/3.0/css/bootstrap.min.css'
		responsive = False
	
	return {
		'responsive': responsive,
		'css_url': css_url,
		'responsive_css_url': responsive_css_url,
		'STATIC_URL': context.get('STATIC_URL')
	}

@register.simple_tag()
def bootstrap_scripts():
	return '<script src="%sbootstrap/%sjs/bootstrap.js"></script>' % (
		settings.STATIC_URL or '/static/',
		getattr(settings, 'BOOTSTRAP_VERSION', '2.3.2').startswith('3.0') and '3.0/' or ''
	)

@register.inclusion_tag('bootstrap/navbar.inc.html', takes_context = True)
def bootstrap_navbar(context):
	context.update(
		{
			'BOOTSTRAP_3': getattr(settings, 'BOOTSTRAP_VERSION', '2.3.2').startswith('3.0'),
			'NAVIGATION': ('bambu.navigation' in settings.INSTALLED_APPS and 'true' or 'false'),
			'INVERSE': getattr(settings, 'BOOTSTRAP_NAVBAR_INVERSE', False),
		}
	)
	
	return context

@register.inclusion_tag('bootstrap/footer.inc.html', takes_context = True)
def bootstrap_footer(context):
	return {
		'NAVIGATION': ('bambu.navigation' in settings.INSTALLED_APPS and 'true' or 'false'),
		'request': context.get('request'),
		'SITE': SITE
	}

@register.simple_tag(takes_context = True)
def bootstrap_title(context, separator = ' | '):
	title_parts = context.get('title_parts')
	
	if title_parts:
		return separator.join(title_parts) + separator + SITE.name
	else:
		return SITE.name

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

@register.tag
def tryload(parser, token):
	bits = token.contents.split()
	if len(bits) >= 4 and bits[-2] == "from":
		try:
			taglib = bits[-1]
			lib = get_library(taglib)
		except InvalidTemplateLibrary as e:
			return LoadNode()
		else:
			temp_lib = Library()
			for name in bits[1:-2]:
				if name in lib.tags:
					temp_lib.tags[name] = lib.tags[name]
					if name in lib.filters:
						temp_lib.filters[name] = lib.filters[name]
				elif name in lib.filters:
					temp_lib.filters[name] = lib.filters[name]
				else:
					return LoadNode()
			parser.add_library(temp_lib)
	else:
		for taglib in bits[1:]:
			try:
				lib = get_library(taglib)
				parser.add_library(lib)
			except InvalidTemplateLibrary as e:
				return LoadNode()
	
	return LoadNode()

@register.tag()
def trymenu(parser, token):
	split = token.contents.split(None)
	tag_name = split.pop(0)
	key = split.pop(0)
	args = split
	
	nodelist = parser.parse(('endtrymenu',))
	parser.delete_first_token()
	
	if 'bambu.navigation' in settings.INSTALLED_APPS:
		from bambu.navigation.templatetags.navigation import CycleNode
		return CycleNode(key, nodelist, ' '.join(args))
	
	return LoadNode()

@register.inclusion_tag('bootstrap/typekit.inc.html')
def typekit():
	return {
		'key': getattr(settings, 'TYPEKIT_KEY', '')
	}