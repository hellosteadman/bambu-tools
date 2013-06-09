from django.db import models
from bambu.bootstrap.fontawesome import ICONS

class Category(models.Model):
	name = models.CharField(max_length = 100)
	slug = models.SlugField(max_length = 100, unique = True)
	order = models.PositiveIntegerField(db_index = True)
	icon = models.CharField(max_length = 30, choices = ICONS, default = u'question-sign')
	
	def __unicode__(self):
		return self.name
	
	@models.permalink
	def get_absolute_url(self):
		return ('faq_topics_category', [self.slug])
	
	class Meta:
		ordering = ('order',)
		verbose_name_plural = 'categories'

class Topic(models.Model):
	question = models.CharField(max_length = 255)
	answer = models.TextField()
	order = models.PositiveIntegerField()
	category = models.ForeignKey(Category, related_name = 'topics')
	icon = models.CharField(max_length = 30, choices = ICONS, default = u'question-sign')
	
	def __unicode__(self):
		return self.question
	
	def get_abslute_url(self):
		return '%s#topic#%d' % (
			self.category.get_absolute_url(), self.pk
		)
	
	class Meta:
		ordering = ('order',)