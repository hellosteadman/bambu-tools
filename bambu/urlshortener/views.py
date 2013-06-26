from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from bambu.urlshortener.models import ShortURL
from warnings import warn

warn('bambu.urlshortener.urls is deprecated. Use bambu.urlshortener.middleware.ShortURLFallbackMiddleware instead.', DeprecationWarning, stacklevel = 2)

@transaction.commit_on_success()
def url(request, slug):
	shortened = get_object_or_404(ShortURL, slug = slug)
	shortened.visits += 1
	shortened.last_visited = now()
	shortened.save()
	
	return HttpResponseRedirect(shortened.url)