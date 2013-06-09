from django.contrib.sites.models import Site

def basics(request):
	return {
		'SITE': Site.objects.get_current()
	}