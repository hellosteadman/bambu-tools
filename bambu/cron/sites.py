from datetime import datetime
from django.utils.timezone import utc
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
		now = datetime.utcnow().replace(tzinfo = utc)
		
		for handler in self._registry.values():
			next = handler.next_run_date()
			if not Job.objects.filter(name = handler).select_for_update(nowait = False).exists():
				Job.objects.create(
					name = handler,
					next_run = next
				)
			else:
				Job.objects.filter(
					name = handler
				).update(
					next_run = next
				)
				
			self.logger.info(
				'%s set to run on %s' % (
					handler, next.strftime('%c')
				)
			)
		
		Job.objects.exclude(
			name__in = [str(n) for n in self._registry]
		).delete()
	
	def run(self, force = False, debug = False):
		from bambu.cron.models import Job
		now = datetime.utcnow().replace(tzinfo = utc)
		
		kwargs = {}
		if not force:
			kwargs['next_run__lte'] = now
		
		for job in Job.objects.filter(running = False, **kwargs).select_for_update(nowait = False):
			handler = self._registry.get(job.name)
			if handler is None:
				job.delete()
				continue
			
			job.running = True
			job.save()
			
			def dorun():
				if handler.transactional:
					with transaction.commit_on_success():
						self.logger.debug('Starting transaction')
						try:
							handler.run(self.logger)
							self.logger.debug('Committing transaction')
						except:
							self.logger.debug('Rolling back transaction')
							raise
				else:
					handler.run(self.logger)
			
			try:
				if not debug:
					try:
						handler.run(self.logger)
					except Exception, ex:
						self.logger.error(
							u'Error running %s: %s' % (
								job, unicode(ex)
							)
						)
				else:
					handler.run(self.logger)
			finally:
				job.next_run = handler.next_run_date()
				job.running = False
				job.save()