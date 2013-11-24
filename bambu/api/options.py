from django.conf.urls import patterns, url, include
from django.utils.functional import curry
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import models, transaction
from django.forms import Form, ModelForm
from django.forms.models import modelform_factory
from django.http import Http404
from bambu.api import helpers
from bambu.api.transformers import library
from bambu.api.exceptions import APIException

class API(object):
	parent = None
	form = Form
	
	def __init__(self, api_site):
		self.api_site = api_site
	
	def get_urls():
		return patterns('')
	
	@property
	def urls(self):
		return self.get_urls()
	
	def get_form(self, request, **kwargs):
		return self.form()

class ModelAPI(API):
	form = ModelForm
	exclude = ()
	fields = ()
	inlines = []
	allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
	allowed_formats = ('xml', 'json')
	raw_id_fields = ()
	readonly_fields = ()
	
	def __init__(self, model, api_site):
		super(ModelAPI, self).__init__(api_site)
		self.model = model
		self.inline_instances = []
		
		for inline_class in self.inlines:
			fks_to_parent = [
				f for f in inline_class.model._meta.fields
				if isinstance(f, models.ForeignKey) and (
					f.rel.to == self.model
					or f.rel.to in self.model._meta.get_parent_list()
				)
			]
			
			if len(fks_to_parent) == 1:
				fk = fks_to_parent[0]
				rel_name = fk.rel.related_name or '%s_set' % (
					inline_class.model._meta.module_name
				)
				
				self.inline_instances.append(
					inline_class(
						inline_class.model, self, fk,
						rel_name, self.api_site
					)
				)
			elif len(fks_to_parent) == 0:
				raise Exception(
					'%s has no ForeignKey to %s' % (
						inline_class.model, self.model
					)
				)
			else:
				raise Exception(
					'%s has more than 1 ForeignKey to %s' % (
						inline_class.model, self.model
					)
				)
	
	@property
	def list_allowed_methods(self):
		return [m for m in self.allowed_methods if m in ('GET', 'POST')]
	
	@property
	def object_allowed_methods(self):
		return [m for m in self.allowed_methods if m in ('GET', 'PUT', 'DELETE')]
	
	def make_example_object(self, model = None, pk = 1):
		from django.contrib.webdesign import lorem_ipsum
		from django.template.defaultfilters import slugify
		import random
		
		model = model or self.model
		opts = model._meta
		fields = (field for field in opts.local_fields + opts.local_many_to_many)
		kwargs = {
			'id': pk
		}
		
		for field in fields:
			if hasattr(field, 'default') and field.default != models.fields.NOT_PROVIDED:
				if isinstance(field, models.ForeignKey):
					value = field.rel.to.objects.get(pk = field.default)
				else:
					value = field.default
			elif hasattr(self, 'make_random_%s' % field.name):
				value = getattr(self, 'make_random_%s' % field.name)()
			else:
				if isinstance(field, models.SlugField):
					value = slugify(lorem_ipsum.words(2, False))
				elif isinstance(field, models.CharField):
					value = lorem_ipsum.words(5, False).capitalize()
				elif isinstance(field, models.TextField):
					value = lorem_ipsum.words(20).capitalize()
				elif isinstance(field, models.IntegerField):
					value = random.randint(1, 500)
				elif isinstance(field, models.ForeignKey):
					if not field.null:
						value = self.make_example_object(field.rel.to)
					else:
						continue
				elif isinstance(field, models.BooleanField):
					value = field.default
				elif isinstance(field, models.DateTimeField):
					value = now()
				elif isinstance(field, models.DateField):
					value = now().date()
				elif isinstance(field, models.FileField):
					value = 'filename.dat'
				elif isinstance(field, models.AutoField):
					continue
				elif isinstance(field, (models.ManyToManyField, models.fields.related.RelatedField)):
					continue
				else:
					raise Exception(
						'Don\'t know how to generate a default value for %s' % field
					)
			
			kwargs[field.name] = value
		
		return model(**kwargs)
	
	def example_list_response(self):
		from bambu.api.serialisers import JSONSerialiser
		
		return JSONSerialiser().serialise(
			[self.make_example_object(pk = i + 1) for i in range(3)]
		)
	
	def example_object_response(self):
		from bambu.api.serialisers import JSONSerialiser
		
		return JSONSerialiser(max_detail_level = 2).serialise(
			self.make_example_object()
		)
	
	def get_urls(self):
		info = self.model._meta.app_label, self.model._meta.module_name
		
		urlpatterns = patterns('',
			url(r'^\.(?P<format>' + '|'.join(self.allowed_formats) + ')$',
				helpers.wrap_api_function(
					self.api_site, self.list_view, 1,
					self.list_allowed_methods, self.prepare_output_data
				),
				name = '%s_%s_list' % info
			),
			url(r'^/(?P<object_id>\d+)\.(?P<format>' + '|'.join(self.allowed_formats) + ')$',
				helpers.wrap_api_function(
					self.api_site, self.object_view, 2,
					self.object_allowed_methods, self.prepare_output_data
				),
				name = '%s_%s_object' % info
			)
		)
		
		for inline in self.inline_instances:
			urlpatterns += patterns('',
				url(
					r'^/(?P<' + inline.rel_field.name + '>\d+)/' + inline.rel_name,
					include(inline.get_urls())
				)
			)
		
		return urlpatterns
	
	def get_form(self, request, obj = None, **kwargs):
		if self.fields is None or not any(self.fields):
			fields = None
		else:
			fields = list(self.fields)
		
		if self.exclude is None:
			exclude = []
		else:
			exclude = list(self.exclude)
		
		exclude.extend(kwargs.get("exclude", []))
		exclude.extend(self.readonly_fields)
		exclude = exclude or None
		
		defaults = {
			'form': self.form,
			'fields': fields,
			'exclude': exclude,
			'formfield_callback': curry(
				self.formfield_for_dbfield,
				request = request
			)
		}
		
		defaults.update(kwargs)
		return modelform_factory(self.model, **defaults)
	
	def formfield_for_dbfield(self, db_field, request, **kwargs):
		if db_field.choices:
			return self.formfield_for_choice_field(db_field, request, **kwargs)
		
		if isinstance(db_field, models.ForeignKey):
			return self.formfield_for_foreignkey(db_field, request, **kwargs)
		
		if isinstance(db_field, models.ManyToManyField):
			return self.formfield_for_manytomany(db_field, request, **kwargs)
		
		return db_field.formfield(**kwargs)
	
	def formfield_for_choice_field(self, db_field, request, **kwargs):
		return db_field.formfield(**kwargs)
	
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		return db_field.formfield(**kwargs)
	
	def formfield_for_manytomany(self, db_field, request, **kwargs):
		if not db_field.rel.through._meta.auto_created:
			return None
		
		return db_field.formfield(**kwargs)
	
	def save_form(self, request, form, obj = None):
		return form.save(commit = False)
	
	def save_object(self, request, obj):
		obj.save()
	
	def prepare_initial_data(self, form_class, obj = None, **kwargs):
		return helpers.form_initial_data(form_class, obj, **kwargs)
	
	def get_query_set(self, request, **kwargs):
		return self.model.objects.filter(**kwargs)
	
	def prepare_output_data(self, request, obj, max_detail_level = 1):
		return library.transform(
			obj, max_detail_level,
			fields = self.fields,
			exclude = self.exclude
		)
	
	def add_field_to_include_filter(self, queryset, field, value):
		if len(value) > 1:
			return queryset.filter(
				**{
					'%s__in' % field: value
				}
			)
		else:
			return queryset.filter(
				**{
					field: value[0]
				}
			)
	
	def add_field_to_exclude_filter(self, queryset, field, value):
		if len(value) > 1:
			return queryset.exclude(
				**{
					'%s__in' % field: value
				}
			)
		else:
			return queryset.exclude(
				**{
					field: value[0]
				}
			)
	
	def list_view(self, request, **kwargs):
		if request.method == 'GET':
			include = {}
			exclude = {}
			fields = [f.name for f in self.model._meta.local_fields]
			order_by = []
			qs = self.get_query_set(request, **kwargs)
			
			for key, value in request.GET.items():
				values = request.GET.getlist(key)
				
				if key == 'order':
					order_by = values
				elif key.startswith('-'):
					if not key[1:] in fields:
						continue
					
					qs = self.add_field_to_exclude_filter(qs, key[1:], values)
				else:
					if key.startswith('+'):
						key = key[1:]
					
					if not key in fields:
						continue
					
					qs = self.add_field_to_include_filter(qs, key, values)
			
			fields = [f.name for f in qs.query.select_fields] + list(qs.query.aggregate_select.keys())
			
			if not any(fields):
				fields = [f.name for f in self.model._meta.local_fields]
			
			if any(include):
				qs = qs.filter(**include)
			
			if any(exclude):
				qs = qs.exclude(**exclude)
			
			if any(order_by):
				orders = []
				
				for order in order_by:
					direction = ''
					
					while order.startswith('-'):
						if direction == '':
							direction = '-'
						else:
							direction = ''
						
						order = order[1:]
					
					if order in fields or order == '?':
						if order == '?' and direction == '-':
							raise APIException(u'Cannot order negatively by random')
						if any(orders):
							raise APIException(u'Cannot order by random when already ordering by other fields')
					else:
						raise APIException(u'Cannot order by %s' % order)
					
					if '?' in orders:
						raise APIException(u'Cannot order by random when already ordering by other fields')
					
					orders.append(direction + order)
				
				qs = qs.order_by(*orders)
			
			return qs
		elif request.method == 'POST':
			form_class = self.get_form(request)
			data = self.prepare_initial_data(form_class, **kwargs)
			
			for key, value in request.POST.items():
				data[key] = value
			
			form = form_class(data, request.FILES)
			if form.is_valid():
				obj = self.save_form(request, form)
				self.save_object(request, obj)
				return obj
			
			errors = []
			for error in form.non_field_errors():
				errors.append(error)
			
			for field in form:
				if field.errors and any(field.errors):
					inline_errors = list([e for e in field.errors])
					
					errors.append(
						{
							field.name: ', '.join(inline_errors)
						}
					)
			
			raise APIException(errors)
	
	def get_object(self, request, object_id, **kwargs):
		try:
			return self.get_query_set(request, **kwargs).get(pk = object_id)
		except self.model.DoesNotExist:
			raise Http404('Object not found.')
	
	def object_view(self, request, object_id, **kwargs):
		obj = self.get_object(request, object_id, **kwargs)
		
		if request.method == 'DELETE':
			with transaction.commit_on_success():
				obj.delete()
				return ['OK']
		elif request.method == 'PUT':
			request.method = "POST"
			request._load_post_and_files()
			request.method = "PUT"
			
			form_class = self.get_form(request, obj)
			data = self.prepare_initial_data(form_class, obj)
			
			for key, value in request.POST.items():
				data[key] = value
			
			form = form_class(data, request.FILES, instance = obj)
			
			if form.is_valid():
				obj = self.save_form(request, form, obj)
				self.save_object(request, obj)
				return obj
			
			errors = []
			for error in form.non_field_errors():
				errors.append(error)
			
			for field in form:
				if field.errors and any(field.errors):
					inline_errors = list([e for e in field.errors])
					
					errors.append(
						{
							field.name: inline_errors
						}
					)
			
			raise Exception(errors)
		
		return obj

class ModelInline(ModelAPI):
	def __init__(self, model, parent, rel_field, rel_name, api_site):
		super(ModelInline, self).__init__(model, api_site)
		self.parent = parent
		self.rel_field = rel_field
		self.rel_name = rel_name
	
	def prepare_initial_data(self, form_class, obj = None, **kwargs):
		data = helpers.form_initial_data(form_class, obj)
		if not obj:
			data[self.rel_field.name] = kwargs.get(self.rel_field.name)
		
		return data