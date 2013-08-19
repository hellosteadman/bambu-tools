"""
Quickly expose your models to a JSON or XML API, authenticated via HTTP or
OAuth.

"""

from bambu.api.options import *
from bambu.api.sites import APISite
from bambu.api.exceptions import APIException
from django.conf import settings
from datetime import datetime

site = APISite()

def autodiscover():
	"""
	Works like ``django.contrib.admin.autodiscover``, running thorugh each of the packages within a
	project's ``INSTALLED_APPS`` setting, to find instances of an ``api`` module which might contain
	calls to ``bambu.api.site.register``.
	
	Unlike ``django.contrib.admin.autodiscover``, you do not need to call this function manually.
	"""
	
	from django.utils.importlib import import_module
	from django.utils.module_loading import module_has_submodule
	from copy import copy, deepcopy
	from bambu.api.endpoints import *
	
	for app in settings.INSTALLED_APPS:
		mod = import_module(app)
		
		try:
			before_import_registry = copy(site._registry)
			import_module('%s.api' % app)
		except:
			site._registry = before_import_registry
			if module_has_submodule(mod, 'api'):
				raise