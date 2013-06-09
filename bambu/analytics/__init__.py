from django.conf import settings
from django.utils.importlib import import_module
from logging import getLogger

PROVIDER = getattr(settings, 'ANALYTICS_PROVIDER', 'bambu.analytics.providers.google.GoogleAnalyticsProvider')
LOGGER = getLogger('bambu.analytics')

def _init_tracker(request):
	if not getattr(request, '_analytics_handler', None):
		module, dot, klass = PROVIDER.rpartition('.')
		module = import_module(module)
		
		ps = getattr(settings,
			'ANALYTICS_SETTINGS', {
				klass: {}
			}
		).get(klass)
		
		klass = getattr(module, klass)
		request._analytics_handler = klass(**ps)

def add_events_from_redirect(request):
	events = request.session.get('bambu.analytics.events', [])
	
	if any(events):
		_init_tracker(request)
		request._analytics_handler.events.extend(
			[e for e in events]
		)
		
		del request.session['bambu.analytics.events']
		request.session.modified = True
		return True
	
	return False

def track_event(request, event, **kwargs):
	_init_tracker(request)
	
	try:
		request._analytics_handler.track(event, **kwargs)
	except Exception, ex:
		LOGGER.error((ex), exc_info = ex)