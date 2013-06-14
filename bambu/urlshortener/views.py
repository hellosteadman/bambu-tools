from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from bambu.urlshortener.models import ShortURL

def url(request, slug):
	shortened = get_object_or_404(ShortURL, slug = slug)
	shortened.visits += 1
	shortened.last_visited = now()
	shortened.save()
	
	return HttpResponseRedirect(shortened.url)