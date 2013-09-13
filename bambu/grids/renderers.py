from django.utils.html import escape
from django.utils.http import urlencode
from django.utils.safestring import SafeString, SafeUnicode
from django.utils import simplejson
from django.conf import settings
from django import forms
from math import floor, ceil

def flatten_attrs(attrs):
	portions = []
	for key, value in attrs.items():
		portions.append(' %s="%s"' % (key, value))
	
	return ''.join(portions)

def render_link(value, url, attrs = {}, safe = False):
	if isinstance(value, (SafeString, SafeUnicode)):
		safe_value = unicode(value)
	elif safe:
		safe_value = unicode(value)
	else:
		safe_value = escape(unicode(value))
	
	return u'<a href="%s"%s>%s</a>' % (
		url, flatten_attrs(attrs), safe_value
	)

class Renderer(object):
	container_tag = 'div'
	item_container_tag = 'dl'
	item_column_tag = 'dt'
	item_value_tag = 'dd'
	
	def __init__(self, grid):
		self.grid = grid
	
	def render_header(self, attrs):
		portions = [u'<%s' % self.container_tag]
		portions.append(flatten_attrs(attrs))
		portions.append('>')
		return ''.join(portions)
	
	def render_footer(self):
		return u'</%s>' % self.container_tag
	
	def is_link_column(self, index, value):
		if self._linked:
			return False
		
		col = self.grid.columns[index]
		if index in self.grid._nonlink_columns:
			return False
		
		if index in self.grid._link_columns:
			return True
		
		if col in ('pk', 'id'):
			return False
		
		if isinstance(value, (SafeString, SafeUnicode)):
			return False
		
		self._linked = True
		return True
	
	def render_value(self, index, value, raw_data):
		if isinstance(value, CheckboxRenderer):
			return SafeString(
				value(self.grid.prefix, self.grid._GET)
			)
		
		if self.is_link_column(index, value):
			if hasattr(raw_data, 'get_absolute_url'):
				return render_link(value, raw_data.get_absolute_url())
			
			if hasattr(self.grid, 'get_absolute_url'):
				return render_link(value, self.grid.get_absolute_url(raw_data))
		
		return unicode(value)
	
	def render_item(self, raw_data, prepared_data, attrs):
		portions = [u'<%s>' % self.item_container_tag]
		self._linked = False
		
		for i, (key, value) in enumerate(prepared_data.items()):
			if self.grid.column_attrs:
				attrs = self.grid.column_attrs[i] or {}
			else:
				attrs = {}
			
			portions.append(
				u'<%(tag)s>%(attrs)s%(key)s</%(tag)s>' % {
					'tag': self.item_column_tag,
					'attrs': flatten_attrs(attrs),
					'key': self.grid.get_friendly_name(key)
				}
			)
			
			portions.append(
				u'<%s>' % self.item_value_tag
			)
			
			if hasattr(self.grid, 'render_%s' % key):
				rendered = getattr(self.grid, 'render_%s' % key)(raw_data)
				if not isinstance(rendered, (SafeString, SafeUnicode)):
					rendered = escape(rendered)
				
				portions.append(rendered)
			else:
				portions.append(
					self.render_value(i, value, raw_data)
				)
			
			portions.append(
				u'</%s>' % self.item_value_tag
			)
		
		portions.append(u'</%s>' % self.item_container_tag)
		portions.append(self.render_actions(raw_data))
		
		return u''.join(portions)
	
	def render_actions(self, raw_data):
		portions = []
		visible_actions = getattr(self.grid, 'visible_actions', 1)
		rendered_dropdown = False
		
		for i, action in enumerate(self.grid.actions):
			if visible_actions > 0:
				portions.append(self.render_action(action, raw_data))
				visible_actions -= 1
				continue
			elif not rendered_dropdown:
				portions.append('<div class="dropdown pull-right">&nbsp;')
				portions.append('<a class="dropdown-toggle btn" role="button" data-toggle="dropdown">')
				portions.append('<i class="icon-cog"></i></a>')
				portions.append('<ul class="dropdown-menu" role="menu">')
				rendered_dropdown = True
			
			portions.append('<li>%s</li>' % self.render_action(action, raw_data, i))
			visible_actions -= 1
		
		if len(self.grid.actions) > 1:
			portions.append('</ul></div>')
		
		return u''.join(portions)
	
	def render_action(self, action, obj, index = 0):
		func = getattr(self.grid, action)
		label = getattr(func, 'friendly_name', action.replace('_', ' ').capitalize())
		perms = getattr(func, 'perms', [])
		bulk_title = getattr(func, 'bulk_title', '')
		
		if self.grid._user:
			for perm in perms:
				if not self.grid._user.has_perm(perm):
					return u''
		
		url = func(obj)
		
		if hasattr(func, 'attrs'):
			attrs = func.attrs
		else:
			attrs = {}
		
		if hasattr(func, 'classes'):
			classes = func.classes
		else:
			classes = (attrs.get('class') or 'btn').split(' ')
		
		if index > 0:
			new_classes = []
			for c in classes:
				if c.startswith('btn-') or c == 'btn':
					continue
			
				new_classes.append(c)
		else:
			new_classes = classes
		
		attrs['class'] = ' '.join(new_classes)
		
		if index == 0 and hasattr(func, 'icon'):
			colour = ''
			if hasattr(func, 'icon_colour'):
				colour = ' icon-%s' % func.icon_colour
			
			label = u'<span class="icon-%s%s"></span> %s' % (func.icon, colour, escape(label))
		else:
			label = escape(label)
		
		return render_link(label, url, attrs, True)
	
	def render_empty(self):
		return u'<div>%s</div>' % self.grid.empty_label
	
	def render(self, attrs):
		portions = [self.render_header(attrs)]
		
		if any(self.grid.renderable_data):
			for raw in self.grid.renderable_data:
				prepared = self.grid.prepare(raw)
				portions.append(self.render_item(raw, prepared))
		else:
			portions.append(self.render_empty())
		
		portions.append(self.render_footer())
		return u''.join(portions)

class TableRenderer(Renderer):
	container_tag = 'table'
	item_container_tag = 'tr'
	item_column_tag = 'th'
	item_value_tag = 'td'
	
	def render_sort_field(self, key):
		sortkey = self.grid.prefix and '%s-order' % (self.grid.prefix) or 'order'
		attrs = {}
		sortable = self.grid.field_is_sortable(key)
		
		if sortable:
			if self.grid.ordering and key in self.grid.ordering:
				urlkey = '-%s' % key
				attrs['class'] = 'order-field active'
			elif self.grid.ordering:
				ordering = [
					f.startswith('-') and f[1:] or f
					for f in self.grid.ordering
				]
				
				if key in ordering:
					urlkey = '%s' % key
					attrs['class'] = 'order-field order-reverse active'
				else:
					urlkey = key
			else:
				urlkey = key
		
		portions = [u'<%s%s>' % (self.item_column_tag, flatten_attrs(attrs))]
		
		if sortable:
			portions.append(
				u'<a href="%s">' % self.grid._context_sensitive_url(
					**{
						sortkey: urlkey
					}
				)
			)
		
		if key == '__select__':
			portions.append(
				CheckboxRenderer()(self.grid.prefix, self.grid._GET)
			)
		else:
			portions.append(self.grid.get_friendly_name(key))
		
		if sortable:
			portions.append(u'</a>')
		
		portions.append(u'</%s>' % self.item_column_tag)
		return u''.join(portions)
	
	def render_header(self, attrs):
		portions = [super(TableRenderer, self).render_header(attrs)]
		portions.append('<thead><tr>')
		
		for key in self.grid.columns:
			portions.append(self.render_sort_field(key))
		
		if any(self.grid.actions):
			portions.append(
				u'<%(tag)s>Actions</%(tag)s>' % {
					'tag': self.item_column_tag
				}
			)
		
		portions.append('</tr></thead><tbody>')
		return u''.join(portions)
	
	def render_item(self, raw_data, prepared_data):
		portions = [u'<%s>' % self.item_container_tag]
		self._linked = False
		
		for i, (key, value) in enumerate(prepared_data.items()):
			if self.grid.column_attrs:
				attrs = self.grid.column_attrs[i] or {}
			else:
				attrs = {}
			
			portions.append(
				u'<%s%s>' % (
					self.item_value_tag,
					flatten_attrs(attrs)
				)
			)
			
			if hasattr(self.grid, 'render_%s' % key):
				rendered = getattr(self.grid, 'render_%s' % key)(raw_data)
				if not isinstance(rendered, (SafeString, SafeUnicode)):
					rendered = escape(rendered)
				
				portions.append(rendered)
			else:
				portions.append(
					self.render_value(i, value, raw_data)
				)
			
			portions.append(u'</%s>' % self.item_value_tag)
		
		if any(self.grid.actions):
			if len(self.grid.column_attrs) > len(self.grid.columns):
				attrs = self.grid.column_attrs[len(self.grid.columns)] or {}
			else:
				attrs = {}
			
			portions.append(
				u'<%s%s>' % (
					self.item_value_tag,
					flatten_attrs(attrs)
				)
			)
			
			portions.append(self.render_actions(raw_data))
			portions.append(u'</%s>' % self.item_value_tag)
			
		portions.append(u'</%s>' % self.item_container_tag)
		return u''.join(portions)
	
	def render_empty(self):
		cols = len(self.grid.columns) + (any(self.grid.actions) and 1 or 0)
		return u'<tr class="empty"><td colspan="%d">%s</td></tr>' % (cols, self.grid.empty_label)
	
	def render_footer(self):
		return u'</tbody>' + super(TableRenderer, self).render_footer()

class PaginationRenderer(object):
	max_pagelinks = getattr(settings, 'GRIDS_PAGINATION_LINKS', 5)
	rpp_options = (10, 20, 50, 100, 'all')
	
	def __init__(self, grid):
		self.grid = grid
	
	def render(self, page):
		portions = [u'<div class="pagination">']
		
		if page.has_other_pages():
			portions.append(u'<ul>')
			key = self.grid.prefix and '%s-page' % self.grid.prefix or 'page'
			
			if page.has_previous():
				portions.append(
					u'<li class="prev"><a href="%s" title="Previous page"><i class="icon-chevron-left"></i></a></li>' % self.grid._context_sensitive_url(
						**{
							key: page.previous_page_number()
						}
					)
				)
			else:
				portions.append(u'<li class="prev disabled"><a><i class="icon-chevron-left"></i></a></li>')
			
			if page.paginator.num_pages > self.max_pagelinks:
				minpage = ceil(float(page.number) - float(self.max_pagelinks) / 2.0)
				maxpage = ceil(float(page.number) + float(self.max_pagelinks) / 2.0)
				
				while minpage < 1.0:
					minpage += 1.0
					maxpage += 1.0
				
				while maxpage > float(page.paginator.num_pages):
					maxpage -= 1.0
					if minpage > 1.0:
						minpage -= 1.0
				
				if page.number > self.max_pagelinks / 2:
					max_after = min(self.max_pagelinks / 2, int(maxpage - page.number))
					max_before = min((self.max_pagelinks - max_after - 1, int(page.number - minpage)))
				else:
					max_before = min(self.max_pagelinks / 2, int(page.number - minpage))
					max_after = min(self.max_pagelinks - max_before - 1, int(maxpage - page.number))
				
				minpage = int(minpage)
				maxpage = int(maxpage)
				pagerange = []
				before = []
				after = []
				
				p = page.number - 1
				while p >= minpage and p > 0:
					before.insert(0, p)
					p -= 1
					if len(before) == max_before:
						break
				
				p = page.number + 1
				while p <= maxpage and p <= page.paginator.num_pages:
					after.append(p)
					p += 1
					
					if len(after) == max_after:
						break
				
				pagerange = before + [page.number] + after
			else:
				pagerange = range(1, page.paginator.num_pages + 1)
			
			if pagerange[0] > 1:
				portions.append('<li><a>...</a></li>')
			
			for i in pagerange:
				portions.append(
					u'<li%s><a href="%s">%d</a></li>' % (
						i == page.number and ' class="active"' or '',
						self.grid._context_sensitive_url(
							**{key: i}
						),
						i
					)
				)
			
			if pagerange[-1] < page.paginator.num_pages:
				portions.append('<li><a>...</a></li>')
			
			if page.has_next():
				portions.append(
					u'<li class="next"><a href="%s" title="Next page"><i class="icon-chevron-right"></i></a></li>' % self.grid._context_sensitive_url(
						**{key: page.next_page_number()}
					)
				)
			else:
				portions.append(u'<li class="next disabled"><a><i class="icon-chevron-right"></i></a></li>')
			
			portions.append(u'</ul>')
		
		options = []
		for option in self.rpp_options[:-1]:
			if page.paginator.count > option:
				options.append(
					{
						'text': unicode(option),
						'selected': self.grid.per_page == option,
						'value': unicode(option)
					}
				)
		
		if any(options):
			options.append(
				{
					'text': u'Show all',
					'selected': self.grid.per_page == -1,
					'value': '-1'
				}
			)
			
			key = self.grid.prefix and '%s-rpp' % self.grid.prefix or 'rpp'
			portions.append('<ul class="pull-right"><li><a title="Rows per page"><i class="icon-table"></i></a></li>')
			
			for option in options:
				portions.append(
					u'<li%s><a class="btn" href="%s">%s</a></li>' % (
						option['selected'] and u' class="active"' or u'',
						self.grid._context_sensitive_url(
							**{
								key: option['value']
							}
						),
						option['text']
					)
				)
			portions.append(u'</ul>')
			
		portions.append(u'<div class="clearfix"></div></div>')
		return ''.join(portions)

class FilterRenderer(object):
	def __init__(self, grid):
		self.grid = grid
	
	def render(self, data, attrs = None):
		if not attrs:
			attrs = {
				'class': 'form-inline clearfix'
			}
		
		attrs['id'] = attrs.get('id',
			self.grid.prefix and ('%s-filterform' % self.grid.prefix) or 'filterform'
		)
		
		attrs['class'] += ' bambu-grid-filter-form';
		
		portions = ['<form %s>' % flatten_attrs(attrs)]
		portions.append(self._render_fields(data))
		portions.append(self._render_hiddenfields(data))
		portions.append('</form>')
		portions.append(self._render_script(attrs['id']))
		
		return ''.join(portions)
	
	def _get_fieldnames(self):
		return [
			self.grid.prefix and '%s-%s' % (self.grid.prefix, n) or n
			for n in self.grid.filter
		]
	
	def _render_fields(self, data):
		fields = ''
		
		for fieldname in self.grid.filter:
			name = self.grid.prefix and '%s-%s' % (self.grid.prefix, fieldname) or fieldname
			value = data.get(name)
			choices = self.grid._get_filter_choices(fieldname)
			
			field = forms.ChoiceField(choices = choices)
			field.widget.choices = [
				('', '--- %s ---' % self.grid.get_friendly_name(fieldname))
			] + field.widget.choices[1:]
			
			fields += field.widget.render(name, value)
		
		return fields
	
	def _render_hiddenfields(self, data):
		preserve = {}
		for key, value in data.items():
			if not key in self._get_fieldnames():
				preserve[key] = value
		
		portions = []
		for item in preserve.items():
			portions.append('<input type="hidden" name="%s" value="%s" />' % item)
		
		return ''.join(portions)
	
	def _render_script(self, form_id):
		portions = []
		
		portions.append('<script>$(document).ready(function() { ')
		portions.append("$('form#%s :input').bind('change'," % form_id)
		portions.append("function(e) { $(this).closest('form').submit();});")
		portions.append('});</script>')
		
		return ''.join(portions)

class ModelFilterRenderer(FilterRenderer):
	def _get_fieldnames(self):
		return [
			self.grid.prefix and '%s-%s' % (self.grid.prefix, n) or n
			for n in self.grid.filter
		] + [
			self.grid.prefix and '%s-search' % (self.grid.prefix) or 'search'
		]
	
	def _render_fields(self, data):
		fields = ''
		if any(self.grid.search):
			name = self.grid.prefix and '%s-search' % (self.grid.prefix) or 'search'
			value = data.get(name)
			
			fields += u'<input name="%(name)s" id="id_%(name)s" type="text"' % {'name': name}
			
			if value:
				fields += u' value="%s"' % value
			
			fields += u' class="pull-right" placeholder="Search %(model)s" autocomplete="off" />' % {
				'model': unicode(self.grid.model._meta.verbose_name_plural)
			}
		
		return fields + super(ModelFilterRenderer, self)._render_fields(data)
	
	def _render_script(self, form_id):
		portions = [super(ModelFilterRenderer, self)._render_script(form_id)]
		
		if any(self.grid.search) and self.grid.search_autocomplete:
			search_id = self.grid.prefix and '%s-search' % (self.grid.prefix) or 'search'
			
			portions.append('<script>$(document).ready(function() { ')
			portions.append(
				"$('form#%s input#id_%s').typeahead({source: %s});" % (
					form_id, search_id, simplejson.dumps(self.grid._get_search_options())
				)
			)
			
			portions.append('});</script>')
		
		return ''.join(portions)

class CheckboxRenderer(object):
	def __init__(self, obj = None):
		self.object = obj
	
	def __call__(self, prefix, GET = {}):
		if self.object:
			pk = getattr(self.object, 'pk', getattr(self.object, 'id'))
			html_name = (prefix and '%s-select[%%s]' % (prefix) or 'select[%%s]') % str(pk)
		else:
			html_name = prefix and '%s-select[__all__]' % prefix or 'select[__all__]'
		
		html_id = 'id_%s' % html_name.replace('[', '_').replace(']', '_')
		html = '<input id="%s" type="checkbox" value="1" name="%s" data-select-prefix="%s"%s />' % (
			html_id, html_name, prefix,
			(GET.get(html_name) == '1' and ' checked' or '')
		)
		
		if not self.object:
			html += '<script>jQuery(document).ready(' \
				'function() {' \
					'$(\'#%s\').bind(\'click\', ' \
						'function() {' \
							'if($(this).is(\':checked\')) {' \
								'$(\'input[type="checkbox"][data-select-prefix=\' + $(this).attr(\'data-select-prefix\') + \']\').not($(this)).attr(\'checked\', \'checked\');' \
							'} else {' \
								'$(\'input[type="checkbox"][data-select-prefix=\' + $(this).attr(\'data-select-prefix\') + \']\').not($(this)).removeAttr(\'checked\');' \
							'}' \
						'}' \
					');' \
				'}' \
			');</script>' % html_id
		
		return html