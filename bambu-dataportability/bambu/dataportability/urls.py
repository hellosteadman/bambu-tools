from django.conf.urls import patterns, url
from bambu.dataportability.views import *
from django.conf import settings

if 'bambu.bootstrap' in settings.INSTALLED_APPS or 'bambu.bootstrap.v2' in settings.INSTALLED_APPS:
	from bambu.bootstrap.v2.decorators import body_classes
elif 'bambu.bootstrap.v3' in settings.INSTALLED_APPS:
	from bambu.bootstrap.v3.decorators import body_classes
else:
	def body_classes(view, *classes):
		return view

urlpatterns = patterns('',
	url(r'^import/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$', body_classes(status, 'dataportability', 'import-status'), {'kind': 'import'}, name = 'import_status'),
	url(r'^export/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$', body_classes(status, 'dataportability', 'export-status'), {'kind': 'export'}, name = 'export_status'),
	url(r'^export/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/download/$', download, name = 'download_export')
)