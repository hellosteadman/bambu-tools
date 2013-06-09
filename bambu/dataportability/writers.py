from django.utils.simplejson import JSONEncoder
from bambu.dataportability.simplexmlwriter import SimpleXMLWriter
import logging

class WriterBase(object):
	def __init__(self, stream, wrapper = None, item = None):
		self.stream = stream
		self.wrapper = wrapper
		self.item_wrapper = item
		self.logger = logging.getLogger('bambu.dataportability')
	
	def start(self):
		raise NotImplementedError('Method not implemented.')
	
	def end(self):
		raise NotImplementedError('Method not implemented.')
	
	def item(self, item):
		raise NotImplementedError('Method not implemented.')
	
	def flush(self):
		raise NotImplementedError('Method not implemented.')
	
	def end_writing(self):
		pass

class XMLWriter(WriterBase):
	def start(self):
		self.writer = SimpleXMLWriter(self.stream)
		if self.wrapper:
			self.writer.start(self.wrapper)
	
	def end(self):
		if self.wrapper:
			self.writer.end()
	
	def item(self, item):
		if self.item_wrapper:
			self.writer.start(self.item_wrapper)
		
		self._item(item)
		if self.item_wrapper:
			self.writer.end(self.item_wrapper)
	
	def _item(self, item):
		if isinstance(item, dict):
			for key, value in item.items():
				if key and value:
					if isinstance(value, (list, tuple)):
						for subvalue in value:
							self.writer.start(key)
							self._item(subvalue)
							self.writer.end(key)
					elif isinstance(value, dict):
						self.writer.start(key)
						self._item(value)
						self.writer.end(key)
					else:
						self.writer.start(key)
						self._item(unicode(value))
						self.writer.end(key)
		else:
			self.writer.data(item)
	
	def flush(self):
		self.writer.flush()

class JSONWriter(WriterBase):
	_written = False
	
	def start(self):
		if self.wrapper:
			self.stream.write('{"%s": ' % self.wrapper)
		
		self.stream.write('[')
	
	def end(self):
		if self._written:
			pos = self.stream.tell()
			self.stream.truncate(pos - 1)
			self.stream.seek(pos - 1)
		
		self.stream.write(']')
		
		if self.wrapper:
			self.stream.write('}')
	
	def item(self, item):
		self.stream.write(
			JSONEncoder().encode(item)
		)
		
		self.stream.write(',')
		self._written = True
	
	def flush(self):
		self.stream.flush()