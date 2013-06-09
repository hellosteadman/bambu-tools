from threading import Thread
import logging

class ParserThread(Thread):
	def __init__(self, parser, data, callback):
		Thread.__init__(self)
		self.parser = parser
		self.data = data
		self.callback = callback
	
	def run(self):
		try:
			data = self.parser._parse(self.data)
			self.callback(data)
		except Exception, ex:
			self.parser.job.updates.error(
				'Error parsing file',
				unicode(ex)
			)

class ParserBase(object):
	def __init__(self, job, threaded = True):
		self.job = job
		self.logger = logging.getLogger('bambu.dataportability')
		self.threaded = threaded
	
	def parse(self, data, callback):
		self.job.updates.info('Started processing file')
		
		if self.threaded:
			thread = ParserThread(self, data, callback)
			thread.start()
		else:
			callback(self._parse(data))
	
	def _parse(self, stream):
		raise NotImplementedError('Method not implemented.')

class XMLParser(ParserBase):
	def _parse(self, stream):
		from xml.etree import ElementTree
		
		tree = ElementTree.parse(stream)
		root = tree.getroot()
		
		def xml_to_dict(element):
			children = element.getchildren()
			d = {}
			
			if children:
				for child in children:
					subchildren = child.getchildren()
					if subchildren:
						if child.tag in d:
							if isinstance(d[child.tag], list):
								d[child.tag].append(
									xml_to_dict(child)
								)
							else:
								d[child.tag] = [d[child.tag], xml_to_dict(child)]
						else:
							d[child.tag] = xml_to_dict(child)
					else:
						if child.tag in d:
							if isinstance(d[child.tag], list):
								d[child.tag].append(child.text)
							else:
								d[child.tag] = [d[child.tag], child.text]
						else:
							d[child.tag] = child.text
			
			return d
		
		children = root.getchildren()
		if children:
			for child in children:
				yield xml_to_dict(child)

class JSONParser(ParserBase):
	def _parse(self, stream):
		from django.utils import simplejson
		return simplejson.load(stream)