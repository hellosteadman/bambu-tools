from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.timezone import utc
from bambu.urlshortener.models import ShortURL
from datetime import datetime

def url(request, slug):
	shortened = get_object_or_404(ShortURL, slug = slug)
	shortened.visits += 1
	shortened.last_visited = datetime.now().replace(tzinfo = utc)
	shortened.save()
	
	return HttpResponseRedirect(shortened.url)