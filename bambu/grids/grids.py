from django.core.paginator import Paginator, EmptyPage
from django.utils.safestring import mark_safe
from django.utils.datastructures import SortedDict
from django.db.models import Model
from django.utils.http import urlencode
from django.conf import settings
from bambu.grids.renderers import *
from hashlib import md5
from copy import deepcopy

PUSHSTATE = getattr(settings, 'GRIDS_PUSHSTATE', False)
AJAX = getattr(settings, 'GRIDS_AJAX', False)

class Grid(object):
	per_page = 10
	paginator = Paginator
	grid_renderer = TableRenderer
	pagination_renderer = PaginationRenderer
	filter_renderer = FilterRenderer
	column_attrs = ()
	actions = ()
	bulk_actions = ()
	columns = ()
	exclude = ()
	attrs = ()
	filter = ()
	search = ()
	search_autocomplete = True
	classes = ('table', 'table-striped', 'table-bordered')
	empty_label = u'There are no items in this view.'
	ordering = None
	
	def __init__(self, request, data, attrs = None, **kwargs):
		super(Grid, self).__init__()
		
		self._link_columns = []
		self._nonlink_columns = []
		self.data = data or []
		self.attrs = attrs or {}
		
		classes = kwargs.get('classes') or self.classes
		attr_classes = self.attrs.get('class', '').split(' ')
		columns = []
		
		for c in classes:
			if not c in attr_classes:
				attr_classes.append(c)
		
		attr_classes.sort()
		
		self.attrs['class'] = ' '.join(attr_classes).strip()
		self.columns = self.get_columns()
		self.prefix = kwargs.get('prefix')
		
		try:
			key = self.prefix and '%s-page' % self.prefix or 'page'
			self.page = int(request.GET.get(key, ''))
		except (TypeError, ValueError):
			self.page = 1
		
		key = self.prefix and '%s-order' % self.prefix or 'order'
		if request.GET.get(key):
		 	if request.GET[key] in self.columns:
				self.ordering = (request.GET[key],)
			elif request.GET[key].startswith('-') and request.GET[key][1:] in self.columns:
				self.ordering = (request.GET[key],)
			
		self._GET = {}
		for key, value in request.GET.items():
			self._GET[key] = value
		
		self._path = request.path
		self._user = getattr(request, 'user', None)
		self._hash = md5('%s|%s' % (self._path, self.prefix)).hexdigest()
		self.ajax = kwargs.get('ajax', AJAX)
		
		if self.ajax:
			if 'bambu.enqueue' in settings.INSTALLED_APPS:
				from bambu.enqueue import enqueue_script_file
				enqueue_script_file(request, settings.STATIC_URL + 'grids/js/base.js')
	
	def get_friendly_name(self, column):
		before, underscores, column = column.rpartition('__')
		
		if column in ('pk', 'id'):
			return '#'
		
		return column.replace('_', ' ').replace('  ', ' ').capitalize()
	
	def get_columns(self):
		if not self.columns:
			columns = []
			for item in self.data:
				if not isinstance(item, dict):
					raise Exception('Data must be a list of dicts')
			
				for key in item.keys():
					if not key in columns and not key in self.exclude:
						columns.append(key)
		else:
			columns = self.columns
		
		return columns
	
	def prepare(self, obj):
		row = SortedDict()
		for i, key in enumerate(self.columns):
			value = obj.get(key)
			
			if value and hasattr(self, 'prepare_%s' % key):
				row[key] = getattr(self, 'prepare_%s' % key)(value)
			else:
				row[key] = self._prepare_value(value)
		
		return row
	
	def _prepare_value(self, value):
		if isinstance(value, Model):
			try:
				return render_link(value, value.get_absolute_url())
			except:
				pass
		
		if callable(value):
			return self._prepare_value(value())
		
		if not value is None:
			return value
		
		return u''
	
	def order(self, data):
		key = self.ordering[0]
		reverse = False
		if key.startswith('-'):
			key = key[1:]
			reverse = True
		
		data = sorted(self.data, key = lambda k: k[key]) 
		if reverse:
			data.reverse()
		
		return data
	
	def field_is_sortable(self, field):
		return field in self.columns
	
	def perform_filter(self, data, **options):
		matching = []
		for item in data:
			for key, value in options:
				if not unicode(item.get(key)) == unicode(value):
					continue
			
			matching.append(matching)
		
		return matching
	
	def get_paginator(self, *args, **kwargs):
		return self.paginator(*args, **kwargs)
	
	@property
	def renderable_data(self):
		if not hasattr(self, '_renderable_data'):
			fieldnames = [
				(n, self.prefix and '%s-%s' % (self.prefix, n) or n)
				for n in self.filter
			]
			
			options = {}
			for (realname, getname) in fieldnames:
				if self._GET.get(getname):
					options[realname] = self._GET[getname]
			
			data = self.perform_filter(self.data, **options)
			
			if self.ordering and any(self.ordering):
				data = self.order(data)
			
			self._paginator = self.get_paginator(data, self.per_page)
			
			try:
				self._page = self._paginator.page(self.page)
			except EmptyPage:
				self._page = self._paginator.page(1)
			
			self._renderable_data = self._page.object_list
		return self._renderable_data
	
	def render(self):
		return self.grid_renderer(self).render(self.attrs)
	
	def pagination(self):
		return self.pagination_renderer(self).render(self._page)
	
	def filtering(self):
		self._validate_filters()
		if len(self.filter) > 0 or len(self.search) > 0:
			return self.filter_renderer(self).render(self._GET)
		
		return mark_safe('')
	
	def _validate_filters(self):
		for filter in self.filter:
			if not filter in self.columns:
				raise Exception('Filter on unknown column "%s" not supported' % filter)
	
	def _get_filter_choices(self, filter):
		choices = []
		for item in self.data:
			value = item.get(filter)
			if value and not value in choices:
				choices.add(Value)
		
		return [(c, c) for c in choices]
	
	def _context_sensitive_url(self, **kwargs):
		get = deepcopy(self._GET)
		get.update(kwargs)
		
		return self._path + '?' + urlencode(get)
	
	def __unicode__(self):
		html = '<div class="bambu-grid-container" id="grid_%s">%s%s%s</div>' % (
			self._hash,
			self.filtering(),
			self.render(),
			self.pagination()
		)
		
		if self.ajax:
			if not PUSHSTATE:
				html += ('<script>$(document).ready(function() { bambu.grids.init(\'%s\', false); });</script>' % self._hash)
			else:
				html += (
					'<script>$(document).ready(function() { ' \
					' bambu.grids.init(\'%(hash)s\', true); ' \
					' window.history.replaceState({grid: \'%(hash)s\'}); ' \
					' $(window).bind(\'popstate\', function(e) {' \
					'  if(e.originalEvent.state && e.originalEvent.state.grid == \'%(hash)s\') {' \
					'   bambu.grids.push(\'%(hash)s\', document.location.toString()); ' \
					'  }' \
					' })' \
					'});</script>' % {
						'hash': self._hash
					}
				)
		
		return mark_safe(html)