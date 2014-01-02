from django.conf.urls import patterns, url
from bambu.pages.views import page

try:
	from bambu.bootstrap.decorators import body_classes
	urlpatterns = patterns('',
		url(r'^(?P<slug>[\/\w-]+)/$', body_classes(page, 'page'), name = 'page')
	)
except ImportError:
	urlpatterns = patterns('',
		url(r'^(?P<slug>[\/\w-]+)/$', page, name = 'page')
	)