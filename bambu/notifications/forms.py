from django import forms
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
from django.utils import simplejson
from bambu.notifications.models import Notification
from bambu.notifications.options import NotificationTemplate
from bambu.notifications.settings import DEFAULT_DELIVERY_METHODS, DELIVERY_METHODS
from copy import copy, deepcopy

def get_notifications(user):
	notifications = {}
	for app in settings.INSTALLED_APPS:
		mod = import_module(app)
		
		try:
			submod = import_module('%s.notifications' % app)
		except:
			if module_has_submodule(mod, 'notifications'):
				raise
			
			continue
		
		for name in dir(submod):
			attr = getattr(submod, name)
			if isinstance(attr, NotificationTemplate):
				if attr.staff_only and not user.is_staff:
					continue
				
				if isinstance(attr.perms, (list, tuple)):
					if any(attr.perms) and not user.has_perms(attr.perms):
						continue
				
				notifications[(app, name)] = attr.label or name.replace('_', ' ').capitalize()
	
	return notifications.items()

def get_method_names():
	names = {}
	
	for (key, klass) in DELIVERY_METHODS:
		module, dot, klass = klass.rpartition('.')
		module = import_module(module)
		names[key] = getattr(module, klass).verbose_name
	
	return names.items()

METHOD_NAMES = get_method_names()

class NotificationsForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		self._notifications = get_notifications(self.user)
		
		kwargs['initial'] = dict(
			[
				('%s.%s' % (m, k), simplejson.loads(v or '[]'))
				for m, k, v in self.user.notification_preferences.values_list('module', 'kind', 'methods')
			]
		)
		
		super(NotificationsForm, self).__init__(*args, **kwargs)
		
		for (mod, key), value in self._notifications:
			self.fields[mod + '.' + key] = forms.MultipleChoiceField(
				label = value,
				choices = METHOD_NAMES,
				widget = forms.CheckboxSelectMultiple,
				required = False,
				initial = self.initial.get(mod + '.' + key, DEFAULT_DELIVERY_METHODS)
			)
	
	def save(self):
		keys = []
		
		for (mod, key), value in self._notifications:
			pref, created = self.user.notification_preferences.get_or_create(
				module = mod,
				kind = key
			)
			
			pref.methods = simplejson.dumps(
				self.cleaned_data.get(mod + '.' + key, [])
			)
			
			pref.save()
		
		return self.user