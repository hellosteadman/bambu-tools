from bambu.dataportability.handlers import *
from bambu.dataportability.parsers import *
from bambu.dataportability.exceptions import *

PARSERS = (
	('XML', ('application/xml', 'text/aml'), 'bambu.dataportability.parsers.XMLParser'),
	('JSON', ('application/json', 'text/javascript'), 'bambu.dataportability.parsers.JSONParser')
)

WRITERS = (
	('XML', 'application/xml',  '.xml', 'bambu.dataportability.writers.XMLWriter'),
	('JSON', 'application/json', '.json', 'bambu.dataportability.writers.JSONWriter')
)

def import_file(*args, **kwargs):
	from bambu.dataportability.models import ImportJob
	return ImportJob.objects.import_file(*args, **kwargs)

def export_file(*args, **kwargs):
	from bambu.dataportability.models import ExportJob
	return ExportJob.objects.export_file(*args, **kwargs)