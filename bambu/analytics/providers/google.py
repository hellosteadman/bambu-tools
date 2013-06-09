from django.template.loader import render_to_string
from django.conf import settings
from bambu.analytics import events
from bambu.analytics.providers import ProviderBase
from copy import copy

class GoogleAnalyticsProvider(ProviderBase):
	EVENT_EVENT = '_trackEvent'
	EVENT_PAGE = '_trackPageview'
	EVENT_TRANSACTION = '_addTrans'
	EVENT_TRANSACTION_ITEM = '_addItem'
	
	def __init__(self, *args, **kwargs):
		super(GoogleAnalyticsProvider, self).__init__(*args, **kwargs)
		self.trans = False
		self.trans_tracked = False
		
		if not 'ID' in self.settings:
			ids = getattr(settings, 'GOOGLE_ANALYTICS_IDS', ())
			if any(ids):
				self.settings['ID'] = ids[0]
	
	def track(self, event, **kwargs):
		if event == events.PAGE:
			self.events.append(
				(self.EVENT_PAGE, ())
			)
		elif event == events.EVENT:
			self.events.append(
				(
					self.EVENT_EVENT,
					(
						kwargs.get('category') or u'',
						kwargs.get('action') or u'',
						kwargs.get('option_label') or u'',
						kwargs.get('option_value') or 0,
						kwargs.get('count_bounces', True) == False
					)
				)
			)
		elif event == events.TRANSACTION:
			self.trans = True
			self.events.append(
				(
					self.EVENT_TRANSACTION,
					(
						kwargs.get('transaction_id'),
						kwargs.get('store') or self.site.name,
						kwargs.get('amount') or 0,
						kwargs.get('tax') or 0,
						kwargs.get('postage') or 0,
						kwargs.get('city') or u'',
						kwargs.get('state') or u'',
						kwargs.get('country') or u''
					)
				)
			)
		elif event == events.TRANSACTION_ITEM:
			if not self.trans:
				raise Exception(
					'Analytics event %s fired before %s' % (
						self.EVENT_TRANSACTION_ITEM,
						self.EVENT_TRANSACTION
					)
				)
			
			self.events.append(
				(
					self.EVENT_TRANSACTION_ITEM,
					(
						kwargs.get('transaction_id'),
						kwargs.get('sku'),
						kwargs.get('product'),
						kwargs.get('category') or u'',
						kwargs.get('amount') or 0,
						kwargs.get('quantity') or 1
					)
				)
			)
		else:
			raise Exception('Unknown analytics event: %s' % event)
	
	def render(self, request):
		if not self.settings.get('ID'):
			raise Exception(u'No Google Analytics ID specified')
		
		queue = []
		for (event, args) in self.events:
			event_args = []
			
			for arg in args:
				if isinstance(arg, (str, unicode)):
					event_args.append("'%s'" % arg)
				elif isinstance(arg, bool):
					event_args.append(arg and 'true' or 'false')
				else:
					event_args.append(arg)
				
			queue.append((event, event_args))
		
		if self.trans and not self.trans_tracked:
			queue.append(('_trackTrans',));
			self.trans_tracked = True
		
		self.events = []
		self.trans = False
		self.trans_tracked = False
		
		return render_to_string(
			'analytics/google.inc.html',
			{
				'id': self.settings['ID'],
				'queue': queue,
				'DEBUG': getattr(settings, 'DEBUG', True)
			}
		)