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
	
	return {
		'css_url': css_url and (settings.MEDIA_URL + css_url) or '',
		'STATIC_URL': context.get('STATIC_URL') or '/static/'
	}

@register.simple_tag()
def bootstrap_scripts():
	js_url = getattr(settings, 'BOOTSTRAP_JS_URL', '')
	
	return '<script src="%s"></script>' % (
		js_url and (
			'%s%s' % ((getattr(settings, 'BOOTSTRAP_CSS_BASE', getattr(settings.MEDIA_URL, '/media/'))), js_url)
		) or (
			'%sbootstrap/js/bootstrap.js' % (settings.STATIC_URL or '/static/')
		)
	)

@register.inclusion_tag('bootstrap/navbar.inc.html', takes_context = True)
def bootstrap_navbar(context):
	context.update(
		{
			'NAVIGATION': ('bambu.navigation' in settings.INSTALLED_APPS and 'true' or 'false'),
			'INVERSE': getattr(settings, 'BOOTSTRAP_NAVBAR_INVERSE', False),
			'FIXED_TOP': getattr(settings, 'BOOTSTRAP_NAVBAR_FIXED_TOP', False),
			'FIXED_BOTTOM': getattr(settings, 'BOOTSTRAP_NAVBAR_FIXED_BOTTOM', False)
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