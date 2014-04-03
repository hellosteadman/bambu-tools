from bambu.ajax.sites import AjaxSite
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
from copy import copy, deepcopy

__version__ = '0.1'
site = AjaxSite()

def autodiscover():
	for app in settings.INSTALLED_APPS:
		mod = import_module(app)

		try:
			before_import_registry = copy(site._registry)
			import_module('%s.ajax' % app)
		except:
			site._registry = before_import_registry
			if module_has_submodule(mod, 'ajax'):
				raise
