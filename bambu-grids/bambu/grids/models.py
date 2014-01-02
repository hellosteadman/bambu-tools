from django.db.models import Model, Manager, ManyToManyField, Q
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
from django.utils.datastructures import SortedDict
from bambu.grids.grids import Grid
from bambu.grids.renderers import ModelFilterRenderer
import shlex

class ModelGrid(Grid):
	model = None
	filter_renderer = ModelFilterRenderer
	columns = ()
	exclude = ()
	search = ()
	column_verbose_names = {}
	select_related = True
	
	def __init__(self, request, data, *args, **kwargs):
		if isinstance(data, Model):
			queryset = data.objects.select_related()
		elif isinstance(data, (Manager, QuerySet)):
			queryset = data.select_related()
		else:
			raise ValueError('Data attribute must extend Model or QuerySet')
		
		if queryset.model != self.model:
			raise ValueError('Data queryset must match the Model defined for this ModelGrid')
		
		exclude = self.exclude or []
		super(ModelGrid, self).__init__(request, queryset, *args, **kwargs)
		
		self.empty_label = u'There are no %s in this view.' % self.model._meta.verbose_name_plural
		if not self.ordering:
			self.ordering = self.model._meta.ordering
	
	def get_columns(self):
		if not any(self.columns):
			opts = self.model._meta
			columns = []
			
			for f in opts.local_fields:
				if f != opts.pk and f.editable and not f.name in self.exclude:
					columns.append(f.name)
		else:
			columns = self.columns
		
		return columns
	
	def get_friendly_name(self, column):
		if column in self.column_verbose_names:
			return self.column_verbose_names[column]
		
		if column == '__unicode__':
			name = f.verbose_name
			
			if name.lower() != name:
				return unicode(name)
			else:
				return unicode(name.capitalize())
		
		if hasattr(self, column):
			func = getattr(self, column)
			if hasattr(func, 'friendly_name'):
				return func.friendly_name
		
		for f in self.model._meta.local_fields:
			if f.name == column:
				name = f.verbose_name
				
				if name.lower() != name:
					return unicode(name)
				else:
					return unicode(name.capitalize())
		
		return super(ModelGrid, self).get_friendly_name(column)
	
	def prepare(self, obj):
		row = SortedDict()
		
		for i, column in enumerate(self.columns):
			if hasattr(obj, column):
				value = getattr(obj, column)
			elif hasattr(self, column):
				col = getattr(self, column)
				if hasattr(col, 'safe') and col.safe:
					value = mark_safe(col(obj))
				else:
					value = col(obj)
				
				if hasattr(col, 'link'):
					if col.link:
						self._link_columns.append(i)
					elif not i in self._nonlink_columns:
						self._nonlink_columns.append(i)
			
			elif isinstance(column, str) and '__' in column:
				parts = column.split('__')
				parent = obj
				
				while len(parts) > 0:
					part = parts.pop(0)
					if hasattr(parent, part):
						if len(parts) > 0:
							parent = getattr(parent, part)
						else:
							value = getattr(parent, part)
					else:
						raise Exception(
							'%s not found in %s or %s' % (
								part, type(obj), type(self)
							)
						)
			else:
				raise Exception(
					'%s not found in %s or %s' % (
						column, type(obj), type(self)
					)
				)
			
			if value and hasattr(self, 'prepare_%s' % column):
				row[column] = getattr(self, 'prepare_%s' % column)(value)
			else:
				row[column] = self._prepare_value(value)
				for field in self.model._meta.local_fields:
					if field.name == column:
						if hasattr(field, 'choices') and hasattr(obj, 'get_%s_display' % column):
							row[column] = self._prepare_value(
								getattr(obj, 'get_%s_display' % column)
							)
						
						break
		
		return row
	
	def field_is_sortable(self, field):
		before, underscores, field = field.rpartition('__')
		
		if field in ('pk', '-pk', 'id', '-id'):
			return True
		
		if field.startswith('-'):
			return field[1:] in [n.name for n in self.model._meta.local_fields]
		
		return field in [n.name for n in self.model._meta.local_fields]
	
	def order(self, data):
		ordering = [
			f for f in self.ordering if self.field_is_sortable(f)
		]
		
		if isinstance(data, (Model, Manager, QuerySet)):
			return data.order_by(*ordering)
		
		return data
	
	def _validate_filters(self):
		fieldnames = [
			f.name for f in self.model._meta.local_fields
		] + [
			f.name for f in self.model._meta.local_many_to_many
		]
		
		for filter in self.filter:
			if not filter in fieldnames:
				raise Exception('Filter on unknown field "%s" not supported' % filter)
	
	def _get_filter_choices(self, filter):
		field = None
		
		for f in self.model._meta.local_fields:
			if f.name == filter:
				field = f
		
		for f in self.model._meta.local_many_to_many:
			if f.name == filter:
				field = f
		
		if field:
			return field.get_choices()
	
	def _get_search_options(self):
		values = []
		values_lowered = []
		
		if len(self.data) > 0:
			for row in self.data.values_list(*self.search).distinct().order_by(*self.search):
				for column in row:
					if column and column.strip() and not column.strip().lower() in values_lowered:
						values.append(column.strip())
						values_lowered.append(column.strip().lower())
		
		return sorted(values)
	
	def search_query_set(self, queryset, criteria):
		q = Q()
		
		try:
			words = [w for w in shlex.split(str(criteria))]
		except:
			words = criteria.split(' ')
		
		for column in self.search:
			for word in words:
				q |= Q(
					**{
						'%s__icontains' % column: word
					}
				)
		
		return queryset.filter(q)
	
	def perform_filter(self, data, **options):
		if isinstance(data, QuerySet):
			data = data.filter(**options)
		
		search = self._GET.get(self.prefix and '%s-search' % (self.prefix) or 'search')
		if any(self.search) and search:
			data = self.search_query_set(data, search)
		
		return data