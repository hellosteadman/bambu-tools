"""
Provides a simple, pluggable system for analytics. Get started by adding
`bambu.analytics` to your `INSTALLED_APPS` list, set
`GOOGLE_ANALYTICS_IDS` to a list or tuple of Urchin tracking IDs (which you
get from Google Analytics, oddly enough), and add
`{% load analytics %}{% tracking %}` in the `<head>` tag of your base
template.

You can also call `bambu.analytics.track_event`, passing in the HTTP request
and the name of the event to track, in a view. This is useful if you want to
track an event before performing a redirect, as it preserves the analytics
JavaScript and waits for the next page load to display it (similar to
Django's messaging system).
"""

from django.conf import settings
from django.utils.importlib import import_module
from logging import getLogger

PROVIDER = getattr(settings, 'ANALYTICS_PROVIDER', 'bambu.analytics.providers.google.GoogleAnalyticsProvider')
LOGGER = getLogger('bambu.analytics')

def _init_tracker(request):
	"""
	Setup tracking on a request
	"""
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
	"""
	Add trakcing events from a previous request on the same session
	to the current event queue for this request
	"""
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
	"""
	Track an analytics event. The list of valid arguments varies depending
	on the event being tracked. Supported events can be found in `bambu.analytics.events`
	"""
	_init_tracker(request)
	
	try:
		request._analytics_handler.track(event, **kwargs)
	except Exception, ex:
		LOGGER.error('Error tracking analytics event', exc_info = True,
			extra = {
				'data': {
					'event': event,
					'args': kwargs
				}
			}
		)