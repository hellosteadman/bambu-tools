from django.conf.urls import patterns, url

urlpatterns = patterns('bambu.fileupload.views',
	url(r'^$', 'upload', name = 'fileupload')
)