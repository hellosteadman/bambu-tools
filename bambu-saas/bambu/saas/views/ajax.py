from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

def _ajax_view(request, field):
	value = request.GET.get('v')
	callback = request.GET.get('callback')
	
	if not value:
		response = 'false'
	else:
		response = User.objects.filter(
			**{
				'%s__iexact' % field: value
			}
		).exists() and 'true' or 'false'
	
	if callback:
		response = '%s(%s)' % (callback, response)
	
	return HttpResponse(response, mimetype = 'application/json')

@never_cache
def username_exists(request):
	return _ajax_view(request, 'username')

@never_cache
def email_exists(request):
	return _ajax_view(request, 'email')