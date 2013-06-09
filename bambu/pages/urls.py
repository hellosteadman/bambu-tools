from django.conf.urls import patterns, url
from bambu.bootstrap.decorators import body_classes
from bambu.pages.views import page

urlpatterns = patterns('',
	url(r'^(?P<slug>[\/\w-]+)/$', body_classes(page, 'page'), name = 'page')
)