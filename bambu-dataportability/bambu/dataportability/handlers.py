from threading import Thread
from bambu.dataportability.exceptions import InvalidFormatException
from django.conf import settings
import logging

class ImportThread(Thread):
	def __init__(self, handler, data, formats, callback = None):
		Thread.__init__(self)
		self.handler = handler
		self.data = data
		self.formats = formats
		self.callback = callback
	
	def run(self):
		run_job = False
		
		try:
			if self.handler.supported_formats:
				for format in self.formats:
					if format in self.handler.supported_formats:
						run_job = True
						break
				
				if not run_job:
					raise InvalidFormatException(
						'No handlers are configured to accept this file format.'
					)
			else:
				run_job = True
			
			if run_job:
				result = self.handler._import(self.data, self.formats)
		except Exception, ex:
			self.handler.job.updates.error(
				'Error importing data',
				unicode(ex)
			)
			
			self.notify(False)
			return
		
		if self.callback:
			self.callback(result)
			self.notify()
	
	def notify(self, success = True):
		if 'bambu.notifications' in settings.INSTALLED_APPS:
			from bambu.notifications import notify
			
			if not success:
				actions = [
					{
						'urlname': 'enquiry',
						'title': 'Contact us with any questions'
					}
				]
			else:
				actions = []
			
			notify(
				'bambu.dataportability.import_%s' % (success and 'success' or 'fail'),
				self.handler.job.user,
				job = self.handler.job,
				actions = actions
			)
		else:
			from bambu.mail import render_to_mail
			
			render_to_mail(
				'Importing %s was %s' % (
					self.handler.job.name,
					(success and 'successful' or 'not successful')
				),
				'dataportability/mail/%s.txt' % (success and 'success' or 'fail'),
				{
					'job': self.handler.job,
					'warnings': self.handler.job.updates.filter(kind = 'warning'),
					'errors': self.handler.job.updates.filter(kind = 'error')
				},
				self.handler.job.user
			)

class ExportThread(Thread):
	def __init__(self, handler, writer, callback):
		Thread.__init__(self)
		self.handler = handler
		self.writer = writer
		self.callback = callback
	
	def run(self):
		count = float(self.handler._export_count())
		
		try:
			self.writer.start()
			for i, result in enumerate(self.handler._export()):
				self.writer.item(result)
				
				self.handler.logger.debug('Progress %d' % self.handler.job.progress)
				self.handler.job.progress = int(float(i + 1) / count * 100.0)
				self.handler.job.save()
				
				self.writer.flush()
			
			self.writer.end()
		except Exception, ex:
			self.handler.job.updates.error(
				'Error exporting data',
				unicode(ex)
			)
			
			self.handler.logger.error('Error exporting data', exc_info = True)
			return
		
		self.callback(self.writer.stream)

class HandlerBase(object):
	supported_formats = None
	export_wrapper = None
	export_item = None
	
	def __init__(self, job, threaded = True):
		self.job = job
		self.logger = logging.getLogger('bambu.dataportability')
		self.threaded = threaded
	
	def start_import(self, data, formats, callback):
		if self.threaded:
			thread = ImportThread(self, data, formats, callback)
			thread.start()
		else:
			run_job = False
			if self.supported_formats:
				for format in formats:
					if format in self.supported_formats:
						run_job = True
						break
				
				if not run_job:
					raise InvalidFormatException(
						'No handlers are configured to accept this file format.'
					)
			else:
				run_job = True
			
			if run_job:
				result = self._import(data, formats)
			
			if callback:
				callback(result)
	
	def start_export(self, writer, callback):
		if self.threaded:
			thread = ExportThread(self, writer, callback)
			thread.start()
		else:
			count = float(self._export_count())
			
			try:
				writer.start()
				for i, result in enumerate(self.handler._export()):
					writer.item(result)
					logger.debug('Progress %d' % self.job.progress)
					self.job.progress = int(float(i + 1) / count * 100.0)
					self.job.save()
					self.flush()
				
				writer.end()
			except Exception, ex:
				self.job.updates.error(
					'Error exporting data',
					unicode(ex)
				)
				
				self.logger.error(ex, exc_info = True)
				return
			
			if callback:
				callback(writer.stream)
	
	def _import(self, data, formats):
		raise NotImplementedError('Method not implemented.')
	
	def _export_count(self):
		return 0
	
	def _export(self):
		raise NotImplementedError('Method not implemented.')