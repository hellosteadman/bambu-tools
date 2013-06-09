from django.db import models

class Country(models.Model):
	name = models.CharField(max_length = 100, db_index = True)
	code = models.CharField(max_length = 2, unique = True)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)