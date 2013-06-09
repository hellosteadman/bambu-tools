from django.db import models
from django.template import Template, Context
from django.template.loader import render_to_string
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils import simplejson
from django.utils.importlib import import_module
from django.utils.safestring import mark_safe
from django.template.defaultfilters import linebreaks, urlize
from bambu.notifications.managers import ContextVariableManager, NotificationManager
from bambu.notifications.options import NotificationTemplate
from bambu.notifications.settings import DEFAULT_DELIVERY_METHODS
from bambu.notifications.tasks import deliver_notification_task
from markdown import markdown
import logging

LOGGER = logging.getLogger('bambu.notifications')

class Notification(models.Model):
	module = models.CharField(max_length = 100, db_index = True)
	kind = models.CharField(max_length = 100, db_index = True)
	happened = models.DateTimeField(auto_now_add = True, db_index = True)
	relevant_to = models.ManyToManyField('auth.User', related_name = 'notifications')
	objects = NotificationManager()
	
	def __unicode__(self):
		return self.kind
	
	@models.permalink
	def get_absolute_url(self):
		return ('notification', [self.pk])
	
	def render(self, *kinds):
		if len(kinds) == 0:
			kinds = ('short_plain', 'short')
		
		module = import_module('%s.notifications' % self.module)
		kind = getattr(module, self.kind)
		if isinstance(kind, NotificationTemplate):
			kind = kind.templates
		
		site = Site.objects.get_current()
		
		context_dict = {
			'MEDIA_URL': settings.MEDIA_URL,
			'STATIC_URL': settings.STATIC_URL,
			'SITE': site
		}
		
		context_dict.update(self.context.as_dict())
		context = Context(context_dict)
		
		for k in kinds:
			if not k in kind:
				continue
			
			template = kind[k]
			if k in ('short', 'short_plain', 'short_html'):
				text = Template(template).render(context)
			elif k in ('long', 'long_plain', 'long_html'):
				text = render_to_string(template, context_dict)
				
				if k == 'long':
					text = markdown(text)
			else:
				continue
			
			if not k.endswith('_plain'):
				if k.endswith('_html'):
					return mark_safe(text)
				else:
					return mark_safe(markdown(text))
			else:
				return text
	
	def render_plain(self):
		return self.render('short_plain')
	
	def render_long(self):
		return self.render('long_html', 'long', 'long_plain')
	
	def deliver(self):
		actions = []
		for action in self.actions.all():
			actions.append(
				(unicode(action), action.title)
			)
		
		relevant_to = self.relevant_to.all().values_list('pk', flat = True)
		
		if 'djcelery' in settings.INSTALLED_APPS:
			deliver_notification_task.delay(
				self.module,
				self.kind,
				self.context.as_dict(),
				actions,
				relevant_to = relevant_to
			)
		else:
			deliver_notification_task(
				module = self.module,
				kind = self.kind,
				context = self.context.as_dict(),
				actions = actions,
				relevant_to = relevant_to
			)
	
	class Meta:
		ordering = ('-happened',)
		get_latest_by = 'happened'
	
	class QuerySet(models.query.QuerySet):
		pass

class Action(models.Model):
	notification = models.ForeignKey(Notification, related_name = 'actions')
	urlname = models.CharField(max_length = 255, db_index = True)
	args = models.TextField(null = True, blank = True)
	kwargs = models.TextField(null = True, blank = True)
	title = models.CharField(max_length = 100)
	order = models.PositiveIntegerField(db_index = True)
	
	def __unicode__(self):
		if not hasattr(self, '___unicode__'):
			site = Site.objects.get_current()
			args = self.args and simplejson.loads(self.args) or []
			kwargs = self.kwargs and simplejson.loads(self.kwargs) or {}
			self.___unicode__ = 'http://%s%s' % (
				site.domain,
				reverse(self.urlname, args = args, kwargs = kwargs)
			)
		
		return self.___unicode__
	
	class Meta:
		ordering = ('order',)

class ContextVariable(models.Model):
	notification = models.ForeignKey(Notification, related_name = 'context')
	content_type = models.ForeignKey('contenttypes.ContentType', related_name = 'notification_contexts')
	object_id = models.PositiveIntegerField(db_index = True)
	name = models.CharField(max_length = 100, db_index = True)
	objects = ContextVariableManager()
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)
		unique_together = ('notification', 'name')
	
	class QuerySet(models.query.QuerySet):
		def as_dict(self):
			d = {}
			
			for var in self.all():
				try:
					d[var.name] = var.content_type.get_object_for_this_type(pk = var.object_id)
				except var.content_type.model_class().DoesNotExist:
					continue
			
			return d

class DeliveryPreference(models.Model):
	user = models.ForeignKey('auth.User', related_name = 'notification_preferences')
	module = models.CharField(max_length = 100)
	kind = models.CharField(max_length = 100)
	methods = models.TextField(default = simplejson.dumps(DEFAULT_DELIVERY_METHODS))
	
	def __unicode__(self):
		return '%s - %s' % (
			self.user.get_full_name() or self.user.username,
			self.kind.replace('_', ' ').capitalize()
		)
	
	class Meta:
		unique_together = ('user', 'module', 'kind')