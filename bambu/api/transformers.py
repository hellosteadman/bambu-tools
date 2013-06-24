from django.db.models import Model, Manager
from django.db.models.query import QuerySet
from django.core.files import File
from datetime import date, datetime, time
import logging

class AlreadyRegistered(Exception):
	pass

class NotRegistered(Exception):
	pass

class Transformer(object):
	def __init__(self, fields = (), exclude = ()):
		self.fields = fields
		self.exclude = exclude
		
	def transform(self, obj, level = 1, max_level = 1):
		return {}

class ModelTransformer(Transformer):
	def transform(self, obj, level = 1, max_level = 1):
		opts = obj._meta
		fields = list(field.name for field in opts.local_fields + opts.local_many_to_many)
		for parent in opts.parents:
			fields += list(field.name for field in parent._meta.local_fields + parent._meta.local_many_to_many)
		
		if any(self.fields):
			fields = [f for f in fields if f in self.fields]
		
		if any(self.exclude):
			fields = [f for f in fields if not f in self.exclude]
		
		d = {}
		for field in fields:
			try:
				value = getattr(obj, field)
			except ValueError:
				continue
			
			if isinstance(value, Model):
				if level >= max_level:
					d[field] = value.pk
				else:
					d[field] = library.transform(value, max_level, level + 1)
			elif isinstance(value, datetime):
				d[field] = value.strftime('%Y-%m-%d %H:%M:%S')
			elif isinstance(value, date):
				d[field] = value.strftime('%Y-%m-%d')
			elif isinstance(value, time):
				d[field] = value.strftime('%H:%M:%S')
			elif isinstance(value, (QuerySet, Manager)):
				if level < max_level:
					d[field] = [
						library.transform(v, max_level, level + 1)
						for v in value.all()
					]
			elif isinstance(value, File):
				try:
					d[field] = value.url
				except ValueError:
					pass
			else:
				d[field] = value
		
		return d

class TransformerLibrary(object):
	_registry = {}
	
	def __init__(self):
		self.logger = logging.getLogger('bambu.api')
	
	def register(self, model, transformer = None, fields = (), exclude = ()):
		if model in self._registry:
			raise AlreadyRegistered('Transformer for model %s already registered.' % model)
		
		if transformer is None:
			transformer = ModelTransformer(
				fields = fields or (),
				exclude = exclude or ()
			)
		
		self._registry[model] = transformer
		return self._registry[model]
	
	def unregister(self, model):
		if not model in self._registry:
			raise NotRegistered('Transformer for model %s not registered.' % model)
		
		del self._registry[model]
	
	def transform(self, obj, max_level, level = 1, fields = (), exclude = ()):
		model = type(obj)
		if not model in self._registry:
			self.register(
				type(obj),
				fields = fields,
				exclude = exclude
			)
		
		return self._registry[model].transform(obj, level = level, max_level = max_level)

library = TransformerLibrary()