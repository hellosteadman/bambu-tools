from django.conf.urls import patterns, url
from bambu.bootstrap.decorators import body_classes
from bambu.dataportability.views import *

urlpatterns = patterns('',
	url(r'^import/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$', body_classes(status, 'dataportability', 'import-status'), {'kind': 'import'}, name = 'import_status'),
	url(r'^export/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$', body_classes(status, 'dataportability', 'export-status'), {'kind': 'export'}, name = 'export_status'),
	url(r'^export/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/download/$', download, name = 'download_export')
)