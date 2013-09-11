from django.db.models import Model
from collections import Iterable
from bambu.api.transformers import library

class Serialiser(object):
	def __init__(self, request = None, processor = None, max_detail_level = 1):
		self.max_detail_level = max_detail_level
		self.processor = processor
		self.request = request
	
	def serialise(self, data):
		raise NotImplementedError('Not implemented.')
	
	def _prepare(self, data):
		if data:
			if isinstance(data, Iterable):
				if not isinstance(data, dict):
					return [
						self._make_dict(v) for v in data
					]
			
			return self._make_dict(data)
		
		return []
	
	def _make_dict(self, obj, level = 1):
		if isinstance(obj, Model):
			if self.processor and level == 1:
				return self.processor(self.request, obj, level)
			else:
				return library.transform(obj, self.max_detail_level)
		elif isinstance(obj, dict):
			return obj
		
		return unicode(obj)

class JSONSerialiser(Serialiser):
	def serialise(self, data):
		from django.utils import simplejson
		
		data = simplejson.dumps(
			self._prepare(data)
		)
		
		if self.request and self.request.GET.get('callback'):
			return '%s(%s)' % (
				self.request.GET['callback'],
				data
			)
		else:
			return data

class XMLSerialiser(Serialiser):
	def _write(self, writer, key, data):
		key_checked = self._check_key(key)
		
		if isinstance(data, dict):
			writer.start(key_checked)
			for (subkey, subdata) in data.items():
				self._write(writer, self._check_key(subkey), subdata)
			writer.end(key_checked)
		elif isinstance(data, list):
			for subdata in data:
				self._write(writer, key_checked, subdata)
		elif not data is None:
			writer.element(key_checked, unicode(data))
	
	def _check_key(self, key):
		if not key:
			return None
		
		if key[0].isdigit():
			return '_%s' % key
		else:
			return key
	
	def serialise(self, data):
		from bambu.api.xml import XMLWriter
		from StringIO import StringIO
		
		data = self._prepare(data)
		string = StringIO()
		writer = XMLWriter(string)
		
		if isinstance(data, dict):
			writer.start('result')
			for (key, subdata) in data.items():
				self._write(writer, key, subdata)
			writer.end('result')
		elif isinstance(data, (list, tuple)):
			writer.start('results')
			for d in data:
				self._write(writer, 'result', d)
			writer.end('results')
		elif isinstance(data, Iterable) and not isinstance(data, (str, unicode)):
			writer.start('results')
			for d in data:
				if isinstance(d, dict):
					writer.start('result')
					for (subkey, subdata) in d.items():
						if not subdata is None:
							self._write(writer, subkey, subdata)
					writer.end('result')
				else:
					writer.element('result', d)
			
			writer.end('results')
		elif not data is None:
			writer.element('result', unicode(data))
		
		string.seek(0)
		return string.read()