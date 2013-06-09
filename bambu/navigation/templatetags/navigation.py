from django.template import Node, Variable, Context, Library, TemplateSyntaxError, VariableDoesNotExist
from django.core.urlresolvers import reverse, resolve
from django.conf import settings
from django.utils.safestring import mark_safe
from bambu.navigation import site, autodiscover, DEFAULT_NAVIGATION_MENUS
from bambu.navigation.auth import *
from copy import deepcopy
import shlex

register = Library()
if not site._discovered:
	autodiscover()

menu_dict = {}
for (menu, partials) in getattr(settings, 'NAVIGATION_MENUS', DEFAULT_NAVIGATION_MENUS):
	menu_dict[menu] = partials

class CycleNode(Node):
	def __init__(self, key, nodelist, args, partial = False):
		self.key = key
		self.nodelist = nodelist
		self.args = args
		self.partial = partial
	
	def render(self, context):
		key = Variable(self.key).resolve(context)
		if not key in menu_dict and not self.partial:
			raise TemplateSyntaxError('Menu %s not found in settings.NAVIGATION_MENUS' % key)
		
		if not self.partial:
			partials = menu_dict[key]
		else:
			partials = [key]
		
		request = context.get('request')
		selection = context.get('menu_selection', '')
		
		args = shlex.split(str(self.args))
		kwargs = {}
		
		for arg in args:
			if '=' in arg:
				eq = arg.find('=')
				
				try:
					kwargs[arg[:eq]] = Variable(arg[eq + 1:]).resolve(context)
				except VariableDoesNotExist:
					if arg[eq + 1:] == 'True' or arg[eq + 1:] == 'False':
						kwargs[arg[:eq]] = arg[eq + 1:] == 'True'
					else:
						kwargs[arg[:eq]] = arg[eq + 1:]
		
		args = [a for a in args if not '=' in args]
		items = []
		
		auth = NAVIGATION_SHOW_ALL
		if 'login' in kwargs:
			if kwargs['login']:
				auth = NAVIGATION_SHOW_AUTHENTICATED 
			else:
				auth = NAVIGATION_SHOW_ANONYMOUS
		
		if not self.partial:
			ilist = site.build(key, auth, request and request.user.is_authenticated() or False, *partials)
		else:
			ilist = site.build_partial(key, auth, request and request.user.is_authenticated() or False)
		
		for item in deepcopy(ilist):
			url = item['url']
			url_name = url[0]
			url_args = []
			url_kwargs = {}
			
			for url_param in url[1:]:
				if isinstance(url_param, dict):
					url_kwargs.update(url_param)
				
				if isinstance(url_param, (list, tuple)):
					url_args.extend(url_param)
			
			url = reverse(url_name, args = url_args, kwargs = url_kwargs)
			if item.get('perms'):
				ignore = False
				if not getattr(request, 'user', None):
					continue
				
				if request.user.is_anonymous():
					continue
				
				for perm in item['perms']:
					if not request.user.has_perm(perm):
						ignore = True
						break
				
				if ignore:
					continue
			
			items.append(
				{
					'url': url,
					'title': kwargs.get('long', False) and item.get('title_long', item['title']) or item['title'],
					'active': selection == item['selection'],
					'description': item.get('description'),
					'highlight': item.get('highlight', False),
					'icon': item.get('icon') and mark_safe('<i class="icon-%s"></i>' % item['icon']) or ''
				}
			)
		
		ret = []
		if 'reverse' in self.args:
			items.reverse()
		
		for i, item in enumerate(items):
			context['item'] = item
			context['forloop'] = {
				'counter': i + 1,
				'counter0': i,
				'revcounter': len(items) - i,
				'revcounter0': len(items) - i - 1,
				'first': i == 0,
				'last': i + 1 == len(items),
				'icon': item.get('icon', None),
				'icon': item.get('icon') and mark_safe('<i class="icon-%s"></i>' % item['icon']) or ''
			}
			
			ret.append(
				self.nodelist.render(context)
			)
		
		if len(items) > 0:
			del(context['item'])
			del(context['forloop'])
		
		return ''.join(ret)

@register.tag('menu')
def do_menu(parser, token):
	split = token.contents.split(None)
	tag_name = split.pop(0)
	key = split.pop(0)
	args = split
	
	nodelist = parser.parse(('endmenu',))
	parser.delete_first_token()
	
	return CycleNode(key, nodelist, ' '.join(args))

@register.tag('menupart')
def do_menupart(parser, token):
	split = token.contents.split(None)
	tag_name = split.pop(0)
	key = split.pop(0)
	args = split
	
	nodelist = parser.parse(('endmenupart',))
	parser.delete_first_token()
	
	return CycleNode(key, nodelist, ' '.join(args), partial = True)