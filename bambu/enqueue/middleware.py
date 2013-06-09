from bambu import cron

cron.autodiscover()
class EnqueueMiddleware(object):
	def process_template_response(self, request, response):
		if not hasattr(response, 'context_data'):
			return response
		
		queues = getattr(request, 'queues', {})
		
		css = list(response.context_data.get('enqueued_styles') or [])
		css.extend(queues.get('css') or [])
		response.context_data['enqueued_styles'] = css
		
		scripts = list(response.context_data.get('enqueued_scripts') or [])
		scripts.extend(queues.get('js') or [])
		response.context_data['enqueued_scripts'] = scripts
		
		return response