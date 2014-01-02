from bambu.analytics import track_event, add_events_from_redirect, events

class AnalyticsMiddleware(object):
	def process_request(self, request):
		if not add_events_from_redirect(request):
			track_event(request, events.PAGE)
	
	def process_response(self, request, response):
		if response.status_code in (301, 302):
			if getattr(request, '_analytics_handler', None):
				if len(request._analytics_handler.events) > 0:
					events = request.session.get('bambu.analytics.events', [])
					events.extend(request._analytics_handler.events)
					
					request.session['bambu.analytics.events'] = events
					request.session.modified = True
		
		return response