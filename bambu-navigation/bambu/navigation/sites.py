from django.utils.datastructures import SortedDict
from bambu.navigation.auth import *
import re, logging

class AlreadyRegistered(Exception):
	pass

class NotRegistered(Exception):
	pass
	
class DoesNotExist(Exception):
	pass

class NavigationSite(object):
	_registry = []
	_instances = SortedDict()
	_partials = []
	_discovered = False
	
	def __init__(self):
		self.logger = logging.getLogger('bambu.navigation')
	
	def register(self, builder):
		if builder in self._registry:
			raise AlreadyRegistered('Builder %s already registered.' % builder)
		
		instance = builder()
		self._registry.append(builder)
		partials = tuple([k for (k, d) in self._partials])
		
		for menu in instance.register_partials():
			key = menu['name']
			menus = self._instances.get(key, [])
			menus.append(instance)
			self._instances[key] = menus
			
			if not key in partials:
				self._partials.append(
					(key, menu.get('description', '(No description)'))
				)
	
	def build(self, name, auth = NAVIGATION_SHOW_ALL, logged_in = False, *partials):
		items = []
		plist = []
		exclude = []
		include = []
		
		for partial in partials:
			if partial.startswith('-'):
				exclude.append(partial[1:])
			else:
				include.append(partial)
		
		for partial in include:
			if '*' in partial:
				expr = '^' + partial.replace('.', '\\.').replace('*', '.*') + '$'
				ex = re.compile(expr)
				
				for n in self._instances.keys():
					if ex.match(n):
						if not n in plist:
							plist.append(n)
				
				continue
			
			if not partial in plist:
				plist.append(partial)
		
		for partial in exclude:
			expr = '^' + partial.replace('.', '\\.').replace('*', '.*') + '$'
			ex = re.compile(expr)
			
			for n in self._instances.keys():
				if ex.match(n):
					if n in plist:
						plist.remove(n)
		
		for partial in plist:
			items.extend(
				self.build_partial(partial, auth, logged_in, name)
			)
		
		return sorted(items, key = lambda k: k.get('order', 0))
	
	def build_partial(self, name, auth = NAVIGATION_SHOW_ALL, logged_in = False, menu_name = None):
		items = []
		exclude = []
		instances = []
		
		for builder in self._instances.get(name, []):
			if not builder in instances:
				instances.append(builder)
		
		ilist = []
		for builder in instances:
			builder.add_to_menu(name, ilist, menu_name = menu_name)
		
		for i in ilist:
			if auth == NAVIGATION_SHOW_ALL:
				if i.get('anon', False):
					if not logged_in:
						items.append(i)
				elif i.get('login'):
					if logged_in:
						items.append(i)
				else:
					items.append(i)
			elif auth == NAVIGATION_SHOW_ANONYMOUS and i.get('anon', True):
				if not i.get('login', False):
					items.append(i)
			elif auth == NAVIGATION_SHOW_ANONYMOUS and not logged_in:
				if not i.get('login', False):
					items.append(i)
			elif auth == NAVIGATION_SHOW_AUTHENTICATED and logged_in:
				if i.get('login', False):
					items.append(i)
		
		return sorted(items, key = lambda k: k.get('order', 0))