from django.db import models

class Job(models.Model):
	next_run = models.DateTimeField()
	name = models.CharField(max_length = 255, unique = True)
	running = models.BooleanField(default = False)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)