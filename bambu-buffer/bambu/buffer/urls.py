from django.conf.urls import patterns, url

urlpatterns = patterns('bambu.buffer.views',
    url('^$', 'profiles', name = 'buffer_profiles'),
    url('^refresh/$', 'refresh', name = 'buffer_refresh'),
    url('^auth/$', 'auth', name = 'buffer_auth'),
    url('^callback/$', 'callback', name = 'buffer_callback')
)
