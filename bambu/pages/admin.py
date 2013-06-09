from django.contrib import admin
from django.utils import simplejson
from django.conf import settings
from django import forms
from bambu.pages.models import Page
from bambu.attachments.admin import AttachmentInline
from bambu.preview.admin import PreviewableModelAdmin
from markitup.widgets import MarkItUpWidget

class PageAdminForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		def add_choices(queryset, indent = 0):
			if self.instance:
				queryset = queryset.exclude(pk = self.instance.pk)
			
			for page in queryset:
				choices.append((page.pk, ('-- ' * indent) + page.name))
				add_choices(page.children.all(), indent + 1)
		
		super(PageAdminForm, self).__init__(*args, **kwargs)
		choices = [('', '---------')]
		queryset = self.fields['parent'].queryset
		add_choices(queryset.root())
		
		self.fields['parent'].widget.choices = choices
		self.fields['body'].widget = MarkItUpWidget()
		self.fields['css'].label = u'Custom CSS'
		self.fields['menu_groups'].help_text = u'A comma-separated name of menu groups'
	
	def save(self, commit = True):
		obj = super(PageAdminForm, self).save(commit = False)
		
		if obj.menu_groups:
			menus = []
			
			for menu in obj.menu_groups.split(','):
				menu = menu.strip()
				
				while menu.startswith('"'):
					menu = menu[1:]
				
				while menu.startswith("'"):
					menu = menu[1:]
				
				while menu.endswith('"'):
					menu = menu[:-1]
				
				while menu.endswith("'"):
					menu = menu[:-1]
				
				menus.append("'%s'" % menu)
			
			obj.menu_groups = ','.join(menus)
		else:
			obj.menu_groups = None
		
		if commit:
			obj.save()
		
		return obj
	
	class Meta:
		model = Page
	
	class Media:
		css = 'bambu.codemirror' in settings.INSTALLED_APPS and {
			'all': ('codemirror/lib/codemirror.css',)
		} or {}
		
		js = 'bambu.codemirror' in settings.INSTALLED_APPS and (
			'codemirror/lib/codemirror.js',
			'codemirror/mode/css/css.js',
			'blog/admin.js'
		) or ()

class PageAdmin(PreviewableModelAdmin):
	list_display = ('link_hierarchical', 'parent', 'order_field')
	prepopulated_fields = {
		'slug': ('name',)
	}
	
	inlines = [AttachmentInline]
	form = PageAdminForm
	
	fieldsets = (
		(
			None,
			{
				'fields': ('name', 'slug', 'parent')
			},
		),
		(
			u'Page content',
			{
				'fields': ('title', 'subtitle', 'body', 'css')
			}
		),
		(
			u'Navigation',
			{
				'fields': ('menu_groups', 'order',)
			}
		)
	)
	
	def link_hierarchical(self, obj):
		spaces = 0
		parent = obj.parent
		while parent:
			spaces += 4
			parent = parent.parent
		
		return ('&nbsp;' * spaces) + obj.name
	link_hierarchical.allow_tags = True
	link_hierarchical.short_description = 'Name'
	link_hierarchical.admin_order_field = 'slug_hierarchical'
	
	def order_field(self, obj):
		return obj.order
	order_field.short_description = 'Order'
	order_field.admin_order_field = 'order_hierarchical'
	
	def save_model(self, request, obj, *args, **kwargs):
		obj.author = request.user
		obj.save()

admin.site.register(Page, PageAdmin)