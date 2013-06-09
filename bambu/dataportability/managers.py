from django.db.models import Manager
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from bambu.dataportability import helpers
from mimetypes import guess_type
import logging

class ImportJobManager(Manager):
	def import_file(self, handler, user, file, content_object):
		mimetype, encoding = guess_type(file.name)
		handlers = getattr(settings, 'DATAPORTABILITY_HANDLERS', [])
		
		return self.create(
			name = file.name,
			data = file,
			handler = handlers[handler],
			parser = helpers.get_parser_for_file(file.name),
			user = user,
			content_type = ContentType.objects.get_for_model(content_object),
			object_id = content_object.pk
		)

class ExportJobManager(Manager):
	def export_file(self, handler, user, extension, content_object):
		handlers = getattr(settings, 'DATAPORTABILITY_HANDLERS', [])
		
		return self.create(
			handler = handlers[handler],
			writer = helpers.get_writer_for_extension(extension),
			user = user,
			content_type = ContentType.objects.get_for_model(content_object),
			object_id = content_object.pk
		)

class StatusManager(Manager):
	def _create(self, kind, text, description = None):
		return self.create(
			kind = kind,
			text = text,
			description = description
		)
	
	def info(self, text, description = None):
		return self._create('info', text, description)
	
	def debug(self, text, description = None):
		return self._create('debug', text, description)
	
	def warning(self, text, description = None):
		return self._create('warning', text, description)
	
	def error(self, text, description = None):
		return self._create('error', text, description)
	
	def success(self, text, description = None):
		return self._create('success', text, description)