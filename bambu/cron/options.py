from django.utils.timezone import get_current_timezone, now
from datetime import datetime, timedelta
from bambu.cron.frequency import *

class CronJob(object):
	frequency = DAY
	interval = 1
	weekday = None
	month = None
	day = None
	hour = None
	minute = None
	second = None
	transactional = True
	
	def __init__(self):
		if self.frequency == MINUTE:
			if self.interval >= 60:
				interval = self.interval / 60
				raise Exception('Set frequency to HOUR and interval to %d' % interval, type(self))
		elif self.frequency == HOUR:
			if self.interval >= 24:
				interval = self.interval / 24
				raise Exception('Set frequency to DAY and interval to %d' % interval, type(self))
		elif self.frequency == DAY:
			if self.interval >= 7:
				interval = self.interval / 7
				raise Exception('Set frequency to WEEK and interval to %d' % interval, type(self))
		elif self.frequency == WEEK:
			if self.interval >= 52:
				interval = self.interval / 52
				raise Exception('Set frequency to WEEK and interval to %d' % interval, type(self))
		elif self.frequency == MONTH:
			if self.interval >= 12:
				interval = self.interval / 12
				raise Exception('Set frequency to YEAR and interval to %d' % interval, type(self))
		elif self.frequency != YEAR:
			raise Exception('Unrecognised frequency %s' % self.frequency, type(self))
		
		if not self.month is None and (self.month < 1 or self.month > 12):
			raise Exception('Month not in valid range', type(self))
		
		if not self.day is None and (self.day < 1 or self.day > 31):
			raise Exception('Day not in valid range', type(self))
		
		if not self.hour is None and (self.hour < 0 or self.hour > 23):
			raise Exception('Hour not in valid range', type(self))
		
		if not self.minute is None and (self.minute < 0 or self.minute > 59):
			raise Exception('Minute not in valid range', type(self))
		
		if not self.second is None and (self.second < 0 or self.second > 59):
			raise Exception('Second not in valid range', type(self))
		
		if not self.weekday is None and (self.weekday < 0 or self.weekday > 6):
			raise Exception('Weekday not in valid range', type(self))
		
		self.module_name = '%s.%s' % (self.__module__, type(self).__name__)
	
	def __str__(self):
		return self.module_name
	
	def next_run_date(self, next = None):
		if next is None:
			next = now()
		
		if self.frequency == -1:
			if next.month == 12:
				next = datetime(next.year + 1, 1, next.day).replace(tzinfo = get_current_timezone())
			else:
				next = datetime(next.year, next.month + 1, next.day).replace(tzinfo = get_current_timezone())
		else:
			next += timedelta(minutes = self.frequency * self.interval)
		
		month = next.month
		day = next.day
		hour = next.hour
		minute = next.minute
		second = 0
		
		if not self.month is None:
			month = self.month
		
		if not self.day is None:
			day = self.day
		
		if not self.hour is None:
			hour = self.hour
		
		if not self.minute is None:
			minute = self.minute
		
		if not self.second is None:
			second = self.second
		
		next = datetime(next.year, month, day, hour, minute, second).replace(
			tzinfo = get_current_timezone()
		)
		
		if not self.weekday is None:
			while next.weekday() != self.weekday:
				next += timedelta(days = 1)
		
		return next
	
	def run(self, logger):
	 	raise NotImplementedError('Method not implemented.')