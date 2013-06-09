from django.utils.importlib import import_module
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.template import Template, Context
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import simplejson
from bambu.notifications.options import NotificationTemplate
from bambu.notifications.settings import DELIVERY_METHODS
import logging

def deliver_notification_task(module, kind, context, actions, relevant_to):
	mod = import_module('%s.notifications' % module)
	kind = getattr(mod, kind)
	site = Site.objects.get_current()
	logger = logging.getLogger('bambu.notifications')
	
	versions = {}
	context_dict = {
		'MEDIA_URL': settings.MEDIA_URL,
		'STATIC_URL': settings.STATIC_URL,
		'SITE': site
	}
	
	context_dict.update(context)
	context = Context(context_dict)
	
	if isinstance(kind, dict):
		kind = NotificationTemplate(**kind)
	elif not isinstance(kind, NotificationTemplate):
		raise Exception('Notifications must be a dict or NotificationTemplate type')
	
	for key, template in kind.templates.items():
		if key in ('short', 'short_plain', 'short_html'):
			versions[key] = Template(template).render(context)
		elif key in ('long', 'long_plain', 'long_html'):
			versions[key] = render_to_string(template, context_dict)
	
	methods = {}
	for key, value in dict(DELIVERY_METHODS).items():
		mod, dot, klass = value.rpartition('.')
		mod = import_module(mod)
		methods[key] = getattr(mod, klass)()
	
	for user in User.objects.filter(pk__in = relevant_to):
		pref, created = user.notification_preferences.get_or_create(
			module = module,
			kind = kind
		)
		
		for key in simplejson.loads(pref.methods or '[]'):
			if key in methods:
				methods[key].deliver(user, versions, actions)
			else:
				logger.warn('Unknown notification delivery preference: %s' % key)

if 'djcelery' in settings.INSTALLED_APPS:
	from celery import task
	deliver_notification_task = task(deliver_notification_task)