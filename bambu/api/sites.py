from django.db.models.base import ModelBase
from django.db import transaction
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.conf import settings

try:
	from django.utils.functional import update_wrapper
except ImportError:
	from functools import update_wrapper

from django.utils.importlib import import_module
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.http import require_POST
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.db.models import get_model
from bambu.api.options import *
from bambu.api.response import APIResponse
from bambu.api import transformers, helpers
from bambu.api.exceptions import APIException
import logging

THROTTLE_REQUESTS = getattr(settings, 'API_THROTTLE_REQUESTS', 10000)
THROTTLE_MINUTES = getattr(settings, 'API_THROTTLE_MINUTES', 60 * 24)

class AlreadyRegistered(Exception):
	pass

class NotRegistered(Exception):
	pass

class APISite(object):
	_registry = {}
	app_name = 'api'
	name = 'api'
	
	def __init__(self):
		self.logger = logging.getLogger('bambu.api')
		
		auth = getattr(settings, 'API_AUTH_BACKEND', 'bambu.api.auth.http.HTTPAuthentication')
		mod, dot, klass = auth.rpartition('.')
		mod = import_module(mod)
		self.auth = getattr(mod, klass)()
	
	def register(self, model_or_iterable, api_class = None, **options):
		if isinstance(model_or_iterable, ModelBase):
			model_or_iterable = [model_or_iterable]
		
		for model in model_or_iterable:
			if model._meta.abstract:
				raise ImproperlyConfigured(
					'The model %s is abstract, so it cannot be registered with the API.' % (
						model.__name__
					)
				)
			
			if model in self._registry:
				raise AlreadyRegistered('Model %s already registered.' % model)
			
			if not api_class:
				api_class = ModelAPI
			
			self._registry[model] = api_class(model, self)
			transformers.library.register(
				model,
				transformers.ModelTransformer(api_class.fields, api_class.exclude)
			)
	
	def unregister(self, model):
		if not model in self._registry:
			raise NotRegistered('Model %s not registered.' % model)
		
		del self._registry[model]
	
	def api_view(self, view, request, format, *args, **kwargs):
		if not getattr(view, '_allow_anonymous', False):
			if not self.auth.authenticate(request):
				return self.auth.challenge(request)
			
			request.user = self.auth.user
		else:
			request.user = AnonymousUser()
		
		if getattr(request, 'app', None):
			if not request.app.log_request():
				return APIResponse(
					format, request,
					Exception(u'Maximum number of requests received in %d minute period' % THROTTLE_MINUTES)
				)
		
		detail_level = kwargs.pop('detail_level', 2)
		processor = kwargs.pop('processor', None)
		
		try:
			data = view(request, *args, **kwargs)
		except APIException, ex:
			return APIResponse(format, request, ex)
		
		return APIResponse(format, request, data,
			detail_level = detail_level,
			processor = processor
		)
	
	def api_page(self, view, request, *args, **kwargs):
		if not getattr(view, '_allow_anonymous', False):
			if not self.auth.authenticate(request):
				return self.auth.challenge(request)
			
			request.user = self.auth.user
		else:
			request.user = AnonymousUser()
		
		if getattr(request, 'app', None):
			if not request.app.log_request():
				return HttpResponseBadRequest(
					u'Maximum number of requests received in %d minute period' % THROTTLE_MINUTES
				)
		
		try:
			return view(request, *args, **kwargs)
		except Exception, ex:
			if settings.DEBUG:
				raise
			
			return HttpResponseBadRequest(
				unicode(ex)
			)
	
	def get_urls(self):
		from django.conf.urls import patterns, url, include
		
		def wrap(view):
			def wrapper(*args, **kwargs):
				return self.api_view(view, *args, **kwargs)
			
			return update_wrapper(wrapper, view)
		
		urlpatterns = patterns('',
			url(
				r'^develop/api/$', self.docs_index_view,
				name = 'doc'
			)
		)
		
		if not self.auth.app_model is None:
			urlpatterns += patterns('',
				url(
					r'^develop/apps/$', login_required(self.apps_view),
					name = 'apps'
				),
				url(
					r'^develop/apps/add/$', require_POST(login_required(self.add_app_view)),
					name = 'add_app'
				),
				url(
					r'^develop/apps/(?P<pk>\d+)/$', login_required(self.edit_app_view),
					name = 'edit_app'
				),
				url(
					r'^develop/apps/(?P<pk>\d+)/delete/$', login_required(self.delete_app_view),
					name = 'delete_app'
				),
			)
		
		urlpatterns += patterns('',
			url(
				r'^develop/api/(?P<app_label>[\w]+)/(?P<model>[\w]+)/$',
				self.docs_model_view,
				name = 'doc_model'
			),
			url(
				r'^develop/api/(?P<app_label>[\w]+)/$',
				self.docs_app_view,
				name = 'doc_appindex'
			),
			url(r'^api/', include(self.auth.get_urls()))
		)
		
		for model, model_api in self._registry.iteritems():
			urlpatterns += patterns('',
				url(
					r'^api/%s/%s' % (
						model._meta.app_label, model._meta.module_name
					),
					include(model_api.urls)
				)
			)
		
		return urlpatterns
	
	@property
	def urls(self):
		return self.get_urls(), self.app_name, self.name
	
	def _docs_list(self):
		resdict = {}
		
		for (model, api) in self._registry.items():
			reslist, app_title = resdict.get(
				model._meta.app_label,
				([], model._meta.app_label.capitalize())
			)
			
			if hasattr(api, 'app_label_verbose'):
				app_title = api.app_label_verbose
			
			reslist.append(
				{
					'name': model._meta.verbose_name_plural,
					'url': reverse(
						'api:doc_model', args = (
							model._meta.app_label,
							model._meta.module_name
						)
					)
				}
			)
			
			resdict[model._meta.app_label] = (reslist, app_title)
		
		for app_label, (reslist, app_title) in resdict.items():
			yield {
				'name': app_title,
				'url': reverse('api:doc_appindex', args = [app_label]),
				'children': reslist
			}
	
	def _format_url(self, url, parent_id = None):
		return url.replace(
			'12345', '<b>&lt;id&gt;</b>'
		).replace(
			'67890', '<b>&lt;%s&gt;</b>' % parent_id
		).replace(
			'xml', '<b>&lt;format&gt;</b>'
		)
	
	def _docs_urls(self, api):
		opts = api.model._meta
		
		if api.parent:
			return {
				'list': {
					'url': self._format_url(
						reverse(
							'api:%s_%s_list' % (opts.app_label, opts.module_name),
							args = [67890, 'xml']
						),
						api.rel_field.name
					),
					'allowed_methods': api.list_allowed_methods,
					'example': {
						'url': reverse(
							'api:%s_%s_list' % (opts.app_label, opts.module_name),
							args = [1, 'json']
						),
						'response': api.example_list_response
					}
				},
				'object': {
					'url': self._format_url(
						reverse(
							'api:%s_%s_object' % (opts.app_label, opts.module_name),
							args = [67890, 12345, 'xml']
						),
						api.rel_field.name
					),
					'allowed_methods': api.object_allowed_methods,
					'example': {
						'url': reverse(
							'api:%s_%s_object' % (opts.app_label, opts.module_name),
							args = [1, 1, 'json']
						),
						'response': api.example_object_response
					}
				}
			}
		else:
			return {
				'list': {
					'url': self._format_url(
						reverse(
							'api:%s_%s_list' % (opts.app_label, opts.module_name),
							args = ['xml']
						)
					),
					'allowed_methods': api.list_allowed_methods,
					'example': {
						'url': reverse(
							'api:%s_%s_list' % (opts.app_label, opts.module_name),
							args = ['json']
						),
						'response': api.example_list_response
					}
				},
				'object': {
					'url': self._format_url(
						reverse(
							'api:%s_%s_object' % (opts.app_label, opts.module_name),
							args = [12345, 'xml']
						)
					),
					'allowed_methods': api.object_allowed_methods,
					'example': {
						'url': reverse(
							'api:%s_%s_object' % (opts.app_label, opts.module_name),
							args = [1, 'json']
						),
						'response': api.example_object_response
					}
				}
			}
	
	def docs_index_view(self, request):
		from django.template.response import TemplateResponse
		
		return TemplateResponse(
			request,
			'api/doc/index.html',
			{
				'title_parts': ('Developer resources',),
				'breadcrumb_trail': (
					('', u'Developer resources'),
				),
				'resources': self._docs_list(),
				'auth': {
					'name': self.auth.verbose_name,
					'doc': helpers.trim_indent(self.auth.__doc__)
				},
				'apps_supported': not self.auth.app_model is None,
				'body_classes': ('api', 'api-docs-index')
			}
		)
	
	def apps_view(self, request):
		from django.template.response import TemplateResponse
		
		AppForm = self.auth.get_editor_form()
		return TemplateResponse(
			request,
			'api/apps/list.html',
			{
				'title_parts': ('Apps', 'Developer resources',),
				'breadcrumb_trail': (
					('../', u'Developer resources'),
					('', u'Apps')
				),
				'resources': self._docs_list(),
				'apps': request.user.owned_apps.all(),
				'app_form': AppForm(),
				'apps_supported': True,
				'body_classes': ('api', 'api-apps')
			}
		)
	
	@transaction.commit_on_success
	def add_app_view(self, request):
		from django.template.response import TemplateResponse
		from django.contrib import messages
		
		AppForm = self.auth.get_editor_form()
		form = AppForm(request.POST)
		
		if form.is_valid():
			app = form.save(commit = False)
			app.admin = request.user
			app.save()
			
			messages.success(request, 'Your app has been updated successfully.')
			return HttpResponseRedirect(
				reverse('api:edit_app', args = [app.pk])
			)
		
		return TemplateResponse(
			request,
			'api/apps/list.html',
			{
				'title_parts': ('Create app', 'Apps', 'Developer resources',),
				'breadcrumb_trail': (
					('../../', u'Developer resources'),
					('../', u'Apps'),
					('', u'Create app')
				),
				'resources': self._docs_list(),
				'app_form': form,
				'apps_supported': True,
				'body_classes': ('api', 'api-apps', 'api-apps-add')
			}
		)
	
	@transaction.commit_on_success
	def edit_app_view(self, request, pk):
		from django.template.response import TemplateResponse
		from django.shortcuts import get_object_or_404
		from django.contrib import messages
		
		App = get_model(*self.auth.app_model.split('.'))
		AppForm = self.auth.get_editor_form()
		
		app = get_object_or_404(App, admin = request.user, pk = pk)
		form = AppForm(instance = app, data = request.POST or None)
		
		if request.method == 'POST' and form.is_valid():
			app = form.save()
			messages.success(request, 'Your app has been updated successfully.')
			return HttpResponseRedirect('../')
		
		return TemplateResponse(
			request,
			'api/apps/edit.html',
			{
				'title_parts': (app.name, 'Apps', 'Developer resources',),
				'breadcrumb_trail': (
					('../../', u'Developer resources'),
					('../', u'Apps'),
					('', app.name)
				),
				'resources': self._docs_list(),
				'app': app,
				'form': form,
				'apps_supported': True,
				'body_classes': ('api', 'api-apps', 'api-apps-edit')
			}
		)
	
	def delete_app_view(self, request, pk):
		from django.template.response import TemplateResponse
		from django.shortcuts import get_object_or_404
		from django.contrib import messages
		
		App = get_model(*self.auth.app_model.split('.'))
		app = get_object_or_404(App, admin = request.user, pk = pk)
		
		if request.GET.get('confirm') == '1':
			with transaction.commit_on_success():
				app.delete()
				messages.success(request, 'Your app has been deleted successfully.')
				return HttpResponseRedirect('../../')
		
		return TemplateResponse(
			request,
			'api/apps/delete.html',
			{
				'title_parts': ('Delete?', app.name, 'Apps', 'Developer resources',),
				'breadcrumb_trail': (
					('../../../', u'Developer resources'),
					('../../', u'Apps'),
					('../', app.name),
					('', 'Delete?')
				),
				'resources': self._docs_list(),
				'app': app,
				'apps_supported': True,
				'body_classes': ('api', 'api-apps', 'api-apps-delete')
			}
		)
	
	def docs_app_view(self, request, app_label):
		from django.template.response import TemplateResponse
		
		apis = []
		app_title = app_label.replace('_', ' ').capitalize()
		
		for model in self._registry.keys():
			if model._meta.app_label == app_label:
				opts = model._meta
				api = self._registry[model]
				
				apis.append(
					{
						'title': unicode(opts.verbose_name_plural.capitalize()),
						'doc': helpers.trim_indent(api.__doc__),
						'url': '%s/' % opts.module_name
					}
				)
				
				if hasattr(api, 'app_label_verbose'):
					app_title = api.app_label_verbose
				
		if not any(apis):
			raise Http404('App not found.')
		
		return TemplateResponse(
			request,
			(
				'api/doc/%s/index.html' % app_label,
				'api/doc/app_index.html'
			),
			{
				'title_parts': (
					app_title,
					'Developer resources'
				),
				'breadcrumb_trail': (
					('../', u'Developer resources'),
					('', app_title)
				),
				'resources': self._docs_list(),
				'name': app_title,
				'apis': apis,
				'apps_supported': not self.auth.app_model is None,
				'body_classes': ('api', 'api-docs-app')
			}
		)
	
	def docs_model_view(self, request, app_label, model):
		from django.template.response import TemplateResponse
		from django.http import Http404
		
		model = get_model(app_label, model)
		if not model:
			raise Http404('Model not found.')
		
		api = self._registry.get(model)
		if not api:
			raise Http404('API for model not found.')
		
		opts = model._meta
		api_title = unicode(opts.verbose_name_plural.capitalize())
		app_title = getattr(api, 'app_label_verbose',
			app_label.replace('_', ' ').capitalize()
		)
		
		inlines = []
		for inline in api.inline_instances:
			inlines.append(
				{
					'name': inline.rel_name.capitalize(),
					'doc': helpers.trim_indent(inline.__doc__),
					'urls': self._docs_urls(inline),
					'verbose_name': inline.model._meta.verbose_name,
					'verbose_name_plural': inline.model._meta.verbose_name_plural,
					'formats': inline.allowed_formats
				}
			)
		
		return TemplateResponse(
			request,
			(
				'api/doc/%s/%s.html' % (app_label, model),
				'api/doc/%s/model.html' % app_label,
				'api/doc/model.html'
			),
			{
				'title_parts': (
					api_title,
					app_title,
					'Developer resources'
				),
				'breadcrumb_trail': (
					('../../', u'Developer resources'),
					('../', app_title),
					('', api_title)
				),
				'doc': helpers.trim_indent(api.__doc__),
				'name': api_title,
				'resources': self._docs_list(),
				'inlines': inlines,
				'urls': self._docs_urls(api),
				'verbose_name': opts.verbose_name,
				'verbose_name_plural': opts.verbose_name_plural,
				'formats': api.allowed_formats,
				'apps_supported': not self.auth.app_model is None,
				'body_classes': ('api', 'api-docs-model')
			}
		)