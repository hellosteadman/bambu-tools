from django.conf.urls import patterns, include, url

urlpatterns = patterns('bambu.jwplayer.views',
	url(r'^(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<field>[\w]+)/$', 'player', name = 'jwplayer')
)