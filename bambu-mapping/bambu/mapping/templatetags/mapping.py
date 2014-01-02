from django import template
from django.template.defaultfilters import escapejs, linebreaks
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.importlib import import_module
from bambu.mapping import PROVIDER
import re, string, random, copy

register = template.Library()
kwarg_re = re.compile(r'^([\w]+)=(.+)$')
decimal_re = re.compile(r'^-?\d+\.\d+$')
map_args = ('lat', 'lon', 'width', 'height', 'zoom', 'callback', 'advanced')
marker_args = ('lat', 'lon', 'title', 'icon', 'content', 'draggable', 'callback')
image_args = ('lat', 'lon', 'width', 'height', 'marker', 'alt')

def shlex(text):
	quotemark = None
	in_quotes = False
	remainder = ''
	portions = []
	last = ''
	
	for c in text:
		if c in ('"', "'"):
			remainder += c
			if not in_quotes:
				if last != '' and last != ' ' and last != '=':
					raise template.TemplateSyntaxError(
						"Could not parse the remainder: '%s' from '%s'" % (remainder, text)
					)
				
				quotemark = c
				in_quotes = True
			elif in_quotes and c == quotemark:
				quotemark = None
				in_quotes = False
		elif c == ' ' and not in_quotes:
			portions.append(remainder)
			remainder = ''
		elif c != '=' and c != '.' and c != '-' and c != '_' and c in string.punctuation and not in_quotes:
			raise template.TemplateSyntaxError(
				"Could not parse the remainder: '%s%s' from '%s'" % (remainder, c, text)
			)
		else:
			remainder += c
		
		last = c
	
	if in_quotes:
		raise template.TemplateSyntaxError(
			"Could not parse the remainder: '%s' from '%s'" % (remainder, text)
		)
	
	if remainder:
		portions.append(remainder)
	
	return portions

def resolve(context, variable):
	if variable.startswith("'") and variable.endswith("'"):
		return variable[1:-1]
	
	if variable.startswith('"') and variable.endswith('"'):
		return variable[1:-1]
	
	if variable == 'True' or variable == 'False':
		return variable == 'True'
	
	if variable == 'None':
		return None
	
	if variable.isdigit():
		return int(variable)
	
	if decimal_re.match(variable):
		return float(variable)
	
	return template.Variable(variable).resolve(context)

def parse_args(bits, name, accepts_kwargs):
	bits = [str(s) for s in shlex(bits)]
	
	args = []
	kwargs = {}
	
	for bit in bits:
		match = kwarg_re.match(bit)
		if match and match.groups():
			key, value = match.groups()
			if not key in accepts_kwargs:
				raise template.TemplateSyntaxError(
					"'%s' received unexpected keyword argument '%s'" % (name, key)
				)
			
			if key in kwargs:
				raise template.TemplateSyntaxError(
					"'%s' received multiple values for keyword argument '%s'" % (name, key)
				)
			
			kwargs[key] = value
		elif any(kwargs):
			raise template.TemplateSyntaxError(
				"'%s' received some positional argument(s) after some "
				"keyword argument(s)" % name
			)
		else:
			args.append(bit)
	
	return args, kwargs

class ParamNode(template.Node):
	def _prepare_args(self, context, name, accept_args):
		kwargs = {}
		
		for i, arg in enumerate(self.args):
			try:
				key = accept_args[i]
			except IndexError:
				raise template.TemplateSyntaxError(
					"'%s' received too many positional arguments" % name
				)
			
			if key in self.kwargs:
				raise template.TemplateSyntaxError(
					"'%s' received multiple values for argument '%s'" % (name, key)
				)
			
			try:
				kwargs[key] = resolve(context, arg)
			except template.VariableDoesNotExist:
				pass
		
		for key, value in self.kwargs.items():
			try:
				kwargs[key] = resolve(context, value)
			except template.VariableDoesNotExist:
				continue
		
		return kwargs

class MapNode(ParamNode):
	def __init__(self, nodelist, *args, **kwargs):
		self.nodelist = nodelist
		self.args = args
		self.kwargs = kwargs
	
	def render(self, context):
		kwargs = copy.deepcopy(getattr(settings, 'MAPPING_SETTINGS', {}))
		request = context.get('request')
		
		kwargs.update(
			self._prepare_args(
				context, 'map',
				accept_args = map_args
			)
		)
		
		while True:
			map_id = kwargs.pop('container', '') or ''.join(
				random.sample(string.letters + string.digits, 25)
			)
			
			if not map_id[0].isdigit():
				break
		
		module, comma, klass = PROVIDER.rpartition('.')
		module = import_module(module)
		klass = getattr(module, klass)
		provider = klass(map_id, **kwargs)
		portions = [provider.add_container()]
		
		if not '_MAPPING_MEDIA' in context:
			if not request or not request.is_ajax():
				for js in getattr(provider.Media, 'js', ()):
					portions.append('<script src="%s"></script>' % js % kwargs)
				
				for css in getattr(provider.Media, 'css', ()):
					portions.append('<link href="%s" rel="stylesheet" />' % css % kwargs)
			
			context['_MAPPING_MEDIA'] = True
		
		portions.append('<script>')
		
		if not request or not request.is_ajax():
			portions.append('$(document).ready(function() {')
		
		portions.append(provider.init_map())
		
		portions.append("if(typeof bambu == 'undefined') { bambu = {}; }")
		portions.append("if(!('mapping' in bambu)) {")
		portions.append('bambu.mapping = {markers: {}};')
		portions.append('}')
		portions.append("bambu.mapping.markers['%s'] = [];" % map_id)
		
		context['_BAMBU_MAPPING_PROVIDER'] = provider
		
		portions.append(
			self.nodelist.render(context)
		)
		
		del context['_BAMBU_MAPPING_PROVIDER']
		
		if kwargs.get('callback'):
			portions.append(
				provider.add_map_callback(kwargs['callback'])
			)
		
		if not request or not request.is_ajax():
			portions.append('});')
		
		portions.append('</script>')
		
		if kwargs.get('advanced'):
			portions.append(
				'<script src="%s?m=%s"></script>' % (
					reverse('bambu_mapping_functions'),
					map_id
				)
			)
		
		return ''.join(portions)

@register.tag('map')
def map_tag(parser, token):
	tag, args = token.contents.split(None, 1)
	
	args, kwargs = parse_args(args, tag, map_args)
	nodelist = parser.parse(('endmap',))
	parser.delete_first_token()
	return MapNode(nodelist, *args, **kwargs)

class MarkerNode(ParamNode):
	def __init__(self, *args, **kwargs):
		self.args = args
		self.kwargs = kwargs
	
	def render(self, context):
		kwargs = self._prepare_args(context, 'map', accept_args = map_args)
		provider = context.get('_BAMBU_MAPPING_PROVIDER')
		
		if not provider:
			raise template.TemplateSyntaxError("'marker' tag must be placed within a 'map' tag")
		
		if self not in context.render_context:
			count = 1
		else:
			count = context.render_context[self]
		
		options = '{%s}' % ', '.join(
			[
				'%s: %s' % v for v in {
					'lat': kwargs.get('lat', 'null'),
					'lon': kwargs.get('lon', 'null'),
					'draggable': kwargs.get('draggable') and 'true' or 'false',
					'title': 'title' in kwargs and ("'%s'" % escapejs(kwargs['title'])) or 'null',
					'icon': 'icon' in kwargs and ("'%s'" % escapejs(kwargs['icon'])) or 'null',
					'content': 'content' in kwargs and (
						"'%s'" % escapejs(
							linebreaks(kwargs['content'])
						)
					) or 'null'
				}.items()
			]
		)
		
		portions = []
		portions.append(
			"bambu.mapping.markers['%s'].push((%s(%s)));" % (
				provider.container_id,
				provider.add_marker(),
				options
			)
		)
		
		if kwargs.get('callback'):
			portions.append(
				provider.add_marker_callback(
					"bambu.mapping.markers['%s'][%d]" % (
						provider.container_id, count - 1
					),
					kwargs['callback']
				)
			)
		
		count += 1
		context.render_context[self] = count
		return ''.join(portions)

@register.tag('marker')
def marker_tag(parser, token):
	tag, args = token.contents.split(None, 1)
	args, kwargs = parse_args(args, tag, marker_args)
	
	return MarkerNode(*args, **kwargs)

@register.simple_tag(takes_context = True)
def map_header(context):
	module, comma, klass = PROVIDER.rpartition('.')
	module = import_module(module)
	klass = getattr(module, klass)
	kwargs = copy.deepcopy(getattr(settings, 'MAPPING_SETTINGS', {}))
	
	portions = []
	for js in getattr(klass.Media, 'js', ()):
		portions.append('<script src="%s"></script>' % js % kwargs)
	
	for css in getattr(klass.Media, 'css', ()):
		portions.append('<link href="%s" rel="stylesheet" />' % css % kwargs)
	
	context['_MAPPING_MEDIA'] = True
	return ''.join(portions)

class ImageNode(ParamNode):
	def __init__(self, *args, **kwargs):
		self.args = args
		self.kwargs = kwargs
	
	def render(self, context):
		kwargs = copy.deepcopy(getattr(settings, 'MAPPING_SETTINGS', {}))
		kwargs.update(
			self._prepare_args(
				context, 'mapimage',
				accept_args = image_args
			)
		)
		
		map_id = ''.join(
			random.sample(string.letters + string.digits, 25)
		)
		
		module, comma, klass = PROVIDER.rpartition('.')
		module = import_module(module)
		klass = getattr(module, klass)
		alt = kwargs.pop('alt', 'Map')
		provider = klass(map_id, **kwargs)
		
		return '<img id="%s" src="%s" alt="%s" />' % (
			map_id, provider.get_image_url(), alt
		)

@register.tag('mapimage')
def map_image_tag(parser, token):
	tag, args = token.contents.split(None, 1)
	args, kwargs = parse_args(args, tag, image_args)
	
	return ImageNode(*args, **kwargs)