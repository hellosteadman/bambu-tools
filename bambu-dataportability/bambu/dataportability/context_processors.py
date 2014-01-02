def importing(request):
	def import_file_formats():
		from django.conf import settings
		from django.utils.importlib import import_module
		from bambu.dataportability import PARSERS
		
		parsers = getattr(settings, 'DATAPORTABILITY_PARSERS', PARSERS)
		supported_formats = []
		handlers = []
		
		for handler in getattr(settings, 'DATAPORTABILITY_HANDLERS', []).values():
			module, dot, klass = handler.rpartition('.')
			module = import_module(module)
			klass = getattr(module, klass)
			handlers.append(klass)
		
		for (name, formats, klass) in parsers:
			for format in formats:
				for handler in handlers:
					if handler.supported_formats:
						if format in handler.supported_formats and not name in supported_formats:
							yield name
					elif not name in supported_formats:
						yield name
	
	def export_file_formats():
		from django.conf import settings
		from bambu.dataportability import WRITERS
		
		writers = getattr(settings, 'DATAPORTABILITY_WRITERS', WRITERS)
		for (name, mimetype, extension, klass) in writers:
			yield (extension, name)
	
	return {
		'import_file_formats': import_file_formats,
		'export_file_formats': export_file_formats
	}