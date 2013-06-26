from django.utils.timezone import now
from django.db import transaction
import logging

class AlreadyRegistered(Exception):
	pass

class NotRegistered(Exception):
	pass

class CronSite(object):
	_registry = {}
	
	def __init__(self):
		self.logger = logging.getLogger('bambu.cron')
	
	def register(self, handler):
		if type(handler) in self._registry:
			raise AlreadyRegistered('Handler %s already registered.' % handler.__name__)
		
		handler = handler()
		self._registry[handler.module_name] = handler
	
	def setup(self):
		from bambu.cron.models import Job
		
		with transaction.commit_on_success():
			for handler in self._registry.values():
				next = handler.next_run_date()
				if not Job.objects.filter(name = handler).exists():
					Job.objects.create(
						name = handler,
						next_run = next
					)
				else:
					Job.objects.filter(
						name = handler
					).select_for_update().update(
						next_run = next
					)
				
				self.logger.info(
					'%s set to run on %s' % (
						handler, next.strftime('%c %z')
					)
				)
			
			Job.objects.exclude(
				name__in = [str(n) for n in self._registry]
			).delete()
	
	def run(self, force = False, debug = False):
		from bambu.cron.models import Job
		
		kwargs = {}
		if not force:
			kwargs['next_run__lte'] = now()
		
		with transaction.commit_on_success():
			for job in Job.objects.filter(running = False, **kwargs).select_for_update():
				handler = self._registry.get(job.name)
				if handler is None:
					job.delete()
		
		for job in Job.objects.filter(running = False, **kwargs).select_for_update():	
			handler = self._registry.get(job.name)
			
			if handler.transactional:
				job.running = True
				job.save()
				
				with transaction.commit_on_success():
					self.logger.debug('Starting transaction')
					try:
						handler.run(self.logger)
						self.logger.debug('Committing transaction')
					except:
						self.logger.debug('Rolling back transaction')
						raise
			else:
				job.running = True
				job.save()
				
				try:
					if not debug:
						try:
							handler.run(self.logger)
						except Exception, ex:
							self.logger.error(
								u'Error running %s' % job,
								exc_info = ex
							)
					else:
						handler.run(self.logger)
				finally:
					job.next_run = handler.next_run_date()
					job.running = False
					job.save()