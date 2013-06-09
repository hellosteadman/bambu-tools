from django.db import models
from django.db.models import get_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import post_delete
from django.dispatch import receiver
from bambu.preview.managers import *
from bambu.preview import helpers
from django.utils import simplejson

class Preview(models.Model):
	content_type = models.ForeignKey(ContentType)
	title = models.CharField(max_length = 300)
	data = models.TextField()
	creator = models.ForeignKey('auth.User', related_name = 'previews', db_index = True)
	created = models.DateTimeField(auto_now_add = True, db_index = True)
	objects = PreviewManager()
	
	def __unicode__(self):
		return self.title
	
	@models.permalink
	def get_absolute_url(self):
		return ('preview', [self.pk])
	
	def make_object(self):
		def _make(data, model):
			fields = helpers.get_serialisable_fields(model)
			kwargs = {}
			
			for field in model._meta.local_fields:
				value = None
			
				if field.name in data:
					value = helpers.unserialise(field, data[field.name])
			
				if value:
					kwargs[field.name] = value
			
			for field in model._meta.local_many_to_many:
				value = None
			
				if field.name in data:
					value = helpers.unserialise(field, data[field.name])
			
				if value:
					kwargs[field.name] = value
			
			obj = kwargs
			
			for key, inlines in data.get('_inlines', {}).items():
				model = get_model(*key.split('.'))
				kk = key.replace('.', '__')
				
				for inline in inlines:
					inline_list = obj.get(kk, [])
					inline_list.append(
						_make(inline, model)
					)
					
					obj[kk] = inline_list
			
			return obj
		
		model = self.content_type.model_class()
		obj = _make(simplejson.loads(self.data), model)
		return obj
	
	class Meta:
		ordering = ('-created',)
		get_latest_by = 'created'

class Attachment(models.Model):
	preview = models.ForeignKey(Preview, related_name = 'attachments')
	file = models.FileField(upload_to = helpers.upload_attachment_file, max_length = 300, db_index = True)
	
	def __unicode__(self):
		return self.file.name

@receiver(post_delete, sender = Attachment)
def attachment_delete(sender, instance, **kwargs):
	try:
		instance.file.delete(False)
	except:
		pass