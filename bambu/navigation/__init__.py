from bambu.navigation.sites import NavigationSite
from bambu.navigation.options import MenuBuilder

DEFAULT_NAVIGATION_MENUS = (
	('navbar', ('*', '-legal', '-api', '-profile')),
	('profile', ('profile', '-legal')),
	('footer', ('legal', 'api'))
)

site = NavigationSite()

def autodiscover():
	from django.conf import settings
	from django.utils.importlib import import_module
	from django.utils.module_loading import module_has_submodule
	from copy import copy, deepcopy
	import bambu.navigation.home
	
	for app in settings.INSTALLED_APPS:
		mod = import_module(app)
		
		try:
			before_import_registry = copy(site._registry)
			import_module('%s.menus' % app)
		except:
			site._registry = before_import_registry
			if module_has_submodule(mod, 'menus'):
				raise
	
	site._discovered = True