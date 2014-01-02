from django.conf import settings
from django.core.files import File
from django.utils.importlib import import_module
from django.utils.timezone import now
from bambu.dataportability import helpers
from tempfile import mkstemp
import os

THREADED = not 'djcelery' in settings.INSTALLED_APPS

def import_task(pk):
	from bambu.dataportability.models import ImportJob
	
	def finished(status = None):
		job.updates.success(u'Finished import')
	
	def process(data):
		job.updates.info(u'Finished processing file')
		
		module, dot, klass = job.handler.rpartition('.')
		module = import_module(module)
		handler = getattr(module, klass)(job, threaded = THREADED)
		
		handler.start_import(data,
			helpers.get_formats_for_parser(job.parser),
			finished
		)
	
	job = ImportJob.objects.get(pk = pk)
	module, dot, klass = job.parser.rpartition('.')
	module = import_module(module)
	parser = getattr(module, klass)(job, threaded = THREADED)
	parser.parse(job.data, process)

def export_task(pk):
	from bambu.dataportability.models import ExportJob
	
	job = ExportJob.objects.get(pk = pk)
	for j in ExportJob.objects.filter(user = job.user):
		if j.progress == 100:
			j.delete()
		elif (now() - job.updated).seconds > 60 * 60:
			j.delete()
	
	def finished(stream):
		stream.seek(0)
		job.data = File(stream)
		job.save()
		job.updates.success(u'Finished export')
	
	handle, filename = mkstemp(
		helpers.get_extension_for_writer(job.writer)
	)
	
	os.close(handle)
	stream = open(filename, 'r+w')
	
	module, dot, klass = job.handler.rpartition('.')
	module = import_module(module)
	handler = getattr(module, klass)(job)
	
	module, dot, klass = job.writer.rpartition('.')
	module = import_module(module)
	writer = getattr(module, klass)(
		stream, handler.export_wrapper,
		handler.export_item
	)
	
	handler.start_export(writer, finished)

if 'djcelery' in settings.INSTALLED_APPS:
	from celery import task
	import_task = task(import_task)
	export_task = task(export_task)