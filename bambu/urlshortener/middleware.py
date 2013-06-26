from bambu.urlshortener.models import ShortURL
from django.http import HttpResponseRedirect
from django.db import transaction
from django.utils.timezone import now

class ShortURLFallbackMiddleware(object):
	def process_response(self, request, response):
		if response.status_code == 404:
			slug = request.path
			if slug.startswith('/'):
				slug = slug[1:]
			
			if slug.endswith('/'):
				slug = slug[:-1]
			
			with transaction.commit_on_success():
				try:
					shortened = ShortURL.objects.get(slug = slug)
				except ShortURL.DoesNotExist:
					return response
				
				shortened.visits += 1
				shortened.last_visited = now()
				shortened.save()
				
				return HttpResponseRedirect(shortened.url)
		
		return response