from django.conf.urls import patterns, url

urlpatterns = patterns('bambu.fileupload.views',
	url(r'^$', 'upload', name = 'fileupload'),
	url(r'^delete/$', 'delete', name = 'fileupload_delete'),
	url(r'^list/$', 'filelist', name = 'fileupload_list')
)