from django.db import models
from django.contrib.contenttypes import generic
from django.template import Template, Context
from bambu.attachments.models import Attachment
from bambu.pages.managers import PageManager
from bambu.preview.models import Preview
import logging

class Page(models.Model):
	name = models.CharField(max_length = 100, db_index = True)
	slug = models.SlugField(max_length = 50, db_index = True)
	slug_hierarchical = models.CharField(max_length = 255, unique = True, editable = False)
	order = models.PositiveIntegerField(default = 0, max_length = 2, db_index = True)
	order_hierarchical = models.CharField(max_length = 255, editable = False)
	author = models.ForeignKey('auth.User', related_name = 'pages', editable = False)
	parent = models.ForeignKey('self', related_name = 'children', null = True, blank = True)
	title = models.CharField(max_length = 255, null = True, blank = True)
	subtitle = models.CharField(max_length = 255, null = True, blank = True)
	body = models.TextField(null = True, blank = True)
	css = models.TextField(null = True, blank = True)
	menu_groups = models.CharField(max_length = 255, null = True, blank = True)
	attachments = generic.GenericRelation(Attachment)
	objects = PageManager()
	
	def __unicode__(self):
		return self.name
	
	def render_css(self):
		template = Template(self.css)
		context = Context(
			{
				'attachments': self.attachments.all(),
				'slug': self.slug,
				'pk': self.pk,
				'id': self.pk
			}
		)
		
		return template.render(context)
	
	def update_navigation(self):
		if self.parent:
			slug_parts = self.parent.slug_hierarchical.split('/')
			order_parts = self.parent.order_hierarchical.split('/')
		else:
			slug_parts = []
			order_parts = []
		
		slug_parts.append(self.slug)
		order_parts.append(str(self.order).zfill(2))
		
		self.slug_hierarchical = '/'.join(slug_parts)
		self.order_hierarchical = '/'.join(order_parts)
	
	@models.permalink
	def get_absolute_url(self):
		return ('page', [self.slug_hierarchical])
	
	def get_root_page(self):
		page = self
		parent = self.parent
		
		while parent:
			page = parent
			parent = parent.parent
			if parent is None:
				break
		
		return page
	
	def save(self, *args, **kwargs):
		self.update_navigation()
		super(Page, self).save(*args, **kwargs)
		
		for child in self.children.all():
			child.update_navigation()
			child.save()
	
	class Meta:
		ordering = ('order_hierarchical',)
	
	class QuerySet(models.query.QuerySet):
		def root(self):
			return self.filter(parent__isnull = True)
		
		def menu(self, name):
			return self.filter(menu_groups__icontains = "'%s'" % name)