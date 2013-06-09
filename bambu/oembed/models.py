from django.db import models
from bambu.oembed.managers import *

class Resource(models.Model):
	url = models.URLField(max_length = 255, db_index = True)
	width = models.PositiveIntegerField()
	html = models.TextField()
	objects = ResourceManager()
	
	def __unicode__(self):
		return self.url
	
	class Meta:
		unique_together = ('url', 'width')