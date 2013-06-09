from bambu.cron.sites import CronSite
from bambu.cron.options import CronJob
from bambu.cron.frequency import *
from bambu.cron.weekdays import *

def autodiscover():
	from django.conf import settings
	from django.utils.importlib import import_module
	from django.utils.module_loading import module_has_submodule
	from copy import copy, deepcopy
	
	for app in settings.INSTALLED_APPS:
		mod = import_module(app)
		
		try:
			before_import_registry = copy(site._registry)
			import_module('%s.cron' % app)
		except:
			site._registry = before_import_registry
			if module_has_submodule(mod, 'cron'):
				raise

site = CronSite()