from django.db.models import Model
from django.db.models.query import QuerySet
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.importlib import import_module
from django.utils import simplejson
from bambu.notifications.models import Notification
from bambu.notifications.options import NotificationTemplate

def notify(module, *users, **kwargs):
	module, dot, kind = module.rpartition('.')
	module_info = import_module('%s.notifications' % module)
	kind_info = getattr(module_info, kind)
	actions = kwargs.pop('actions', [])
	
	with transaction.commit_on_success():
		notification = Notification.objects.create(
			module = module,
			kind = kind
		)
		
		for user in users:
			notification.relevant_to.add(user)
		
		for key, value in kwargs.items():
			notification.context.create(
				content_type = ContentType.objects.get_for_model(value),
				object_id = value.pk,
				name = key
			)
		
		for i, action in enumerate(actions):
			notification.actions.create(
				urlname = action['urlname'],
				args = simplejson.dumps(list(action.get('args') or [])),
				kwargs = simplejson.dumps(dict(action.get('kwargs') or {})),
				title = action['title'],
				order = i
			)
	
	notification.deliver()
	return notification