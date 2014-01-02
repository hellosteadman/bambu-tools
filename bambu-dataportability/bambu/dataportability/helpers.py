from django.utils.importlib import import_module
from django.conf import settings
from bambu.dataportability import PARSERS, WRITERS
from bambu.dataportability.exceptions import *
from mimetypes import guess_type, guess_all_extensions
from os import path
from uuid import uuid4

def upload_job_data(instance, filename):
	return '%s%s' % (
		str(uuid4()), path.splitext(filename)[-1]
	)

def get_parser_for_format(format):
	parsers = getattr(settings, 'DATAPORTABILITY_PARSERS', PARSERS)
	
	for (name, formats, klass) in parsers:
		if format in formats:
			return klass
	
	raise Exception('No parser found for format %s' % format)

def get_formats_for_parser(parser):
	parsers = getattr(settings, 'DATAPORTABILITY_PARSERS', PARSERS)
	
	for (name, formats, klass) in parsers:
		if klass == parser:
			return formats
	
	raise InvalidFormatException('This file format is not supported.')

def get_extension_for_writer(writer):
	writers = getattr(settings, 'DATAPORTABILITY_WRITERS', WRITERS)
	
	for (name, mimetype, extension, klass) in writers:
		if klass == writer:
			return extension

def get_parser_for_file(filename):
	mimetype, encoding = guess_type(filename)
	if not mimetype:
		raise InvalidFormatException('File format not recognised.')
	
	parsers = getattr(settings, 'DATAPORTABILITY_PARSERS', PARSERS)
	handlers = []
	supported_handlers = 0
	
	for handler in getattr(settings, 'DATAPORTABILITY_HANDLERS', []).values():
		module, dot, klass = handler.rpartition('.')
		module = import_module(module)
		klass = getattr(module, klass)
		
		if klass.supported_formats:
			if mimetype in klass.supported_formats:
				supported_handlers += 1
		else:
			supported_handlers += 1
	
	if supported_handlers > 0:
		return get_parser_for_format(mimetype)
	
	raise InvalidFormatException('This file format is not supported.')

def get_writer_for_extension(extension):
	writers = getattr(settings, 'DATAPORTABILITY_WRITERS', WRITERS)
	
	for (name, mimetype, ext, klass) in writers:
		if ext == extension:
			return klass
	
	raise InvalidFormatException('This file format is not supported.')