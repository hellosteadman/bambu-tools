from django.conf.urls import patterns, include, url
from bambu import api

api.autodiscover()
urlpatterns = patterns('bambu.api.views',
	url(r'^', include(api.site.urls))
)