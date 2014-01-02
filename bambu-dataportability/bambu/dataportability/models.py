from django.db import models
from django.db.models.signals import pre_delete
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.timezone import now
from uuid import uuid4
from bambu.dataportability import helpers, receivers
from bambu.dataportability.managers import *
from bambu.dataportability.tasks import import_task, export_task
import os, logging

LOGGER = logging.getLogger('bambu.dataportability')

if 'bambu.pusher' in settings.INSTALLED_APPS:
	from bambu.pusher import push
else:
	def push(*args, **kwargs):
		LOGGER.warn('Pusher not installed')

class Job(models.Model):
	started = models.DateTimeField(auto_now_add = True, db_index = True)
	name = models.CharField(max_length = 255)
	updated = models.DateTimeField(auto_now_add = True, db_index = True)
	guid = models.CharField(max_length = 36, unique = True)
	handler = models.CharField(max_length = 255)
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField(db_index = True)
	content_object = generic.GenericForeignKey()
	
	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		if not self.guid:
			self.guid = unicode(uuid4())
		
		super(Job, self).save(*args, **kwargs)
	
	class Meta:
		abstract = True

class Status(models.Model):
	updated = models.DateTimeField(auto_now_add = True, auto_now = True, db_index = True)
	text = models.CharField(max_length = 255)
	description = models.TextField(null = True, blank = True)
	kind = models.CharField(max_length = 10, db_index = True,
		choices = (
			('info', u'Info'),
			('debug', u'Debug'),
			('warning', u'Warning'),
			('error', u'Error'),
			('success', u'Success')
		)
	)
	
	objects = StatusManager()
	
	def __unicode__(self):
		return self.text
	
	def save(self, *args, **kwargs):
		self.job.updated = now()
		super(Status, self).save(*args, **kwargs)
	
	class Meta:
		abstract = True

class ImportJob(Job):
	data = models.FileField(
		storage = FileSystemStorage(location = settings.DATAPORTABILITY_IMPORT_ROOT),
		upload_to = helpers.upload_job_data
	)
	
	user = models.ForeignKey('auth.User', related_name = 'imports')
	parser = models.CharField(max_length = 255)
	
	objects = ImportJobManager()
	
	@models.permalink
	def get_absolute_url(self):
		return ('import_status', [self.guid])
	
	def start(self):
		if 'djcelery' in settings.INSTALLED_APPS:
			import_task.delay(self.pk)
		else:
			import_task(self.pk)
	
	class Meta:
		ordering = ('-updated',)
		get_latest_by = 'updated'
		db_table = 'dataportability_import'

class ImportStatus(Status):
	job = models.ForeignKey(ImportJob, related_name = 'updates')
	
	def save(self, *args, **kwargs):
		super(ImportStatus, self).save(*args, **kwargs)
		
		if self.kind == 'debug':
			return
		
		push(
			channel = 'bambu.dataportability.%d' % self.job.pk,
			event = 'update',
			kind = self.kind,
			text = self.text,
			description = self.description
		)
	
	class Meta:
		ordering = ('updated', 'id')
		get_latest_by = 'updated'
		db_table = 'dataportability_import_status'

class ExportJob(Job):
	data = models.FileField(
		storage = FileSystemStorage(location = settings.DATAPORTABILITY_EXPORT_ROOT),
		upload_to = helpers.upload_job_data, null = True, blank = True
	)
	
	user = models.ForeignKey('auth.User', related_name = 'exports')
	writer = models.CharField(max_length = 255)
	progress = models.PositiveIntegerField(default = 0)
	
	objects = ExportJobManager()
	
	def save(self, *args, **kwargs):
		if not self.name:
			self.name = '%s_%d_%s%s' % (
				self.content_type.model,
				self.object_id,
				now().strftime('%Y-%m-%d'),
				helpers.get_extension_for_writer(self.writer)
			)
		
		if self.pk:
			old = ExportJob.objects.get(pk = self.pk)
			dopush = self.progress > old.progress
		else:
			dopush = False
		
		super(ExportJob, self).save(*args, **kwargs)
		
		if dopush:
			push(
				channel = 'bambu.dataportability.%d' % self.pk,
				event = 'progress',
				progress = self.progress
			)
	
	@models.permalink
	def get_absolute_url(self):
		return ('export_status', [self.guid])
	
	def start(self):
		if 'djcelery' in settings.INSTALLED_APPS:
			export_task.delay(self.pk)
		else:
			export_task(self.pk)
	
	class Meta:
		ordering = ('-updated',)
		get_latest_by = 'updated'
		db_table = 'dataportability_export'

class ExportStatus(Status):
	job = models.ForeignKey(ExportJob, related_name = 'updates')
	
	def save(self, *args, **kwargs):
		super(ExportStatus, self).save(*args, **kwargs)
		
		if self.kind == 'debug':
			return
		
		if self.kind == 'success':
			push(
				channel = 'bambu.dataportability.%d' % self.job.pk,
				event = 'file',
				url = reverse('download_export', args = [self.job.guid])
			)
			
			return
		
		push(
			channel = 'bambu.dataportability.%d' % self.job.pk,
			event = 'update',
			kind = self.kind,
			text = self.text,
			description = self.description,
		)
	
	class Meta:
		ordering = ('updated', 'id')
		get_latest_by = 'updated'
		db_table = 'dataportability_export_status'

pre_delete.connect(receivers.pre_import_delete, sender = ImportJob)
pre_delete.connect(receivers.pre_export_delete, sender = ExportJob)