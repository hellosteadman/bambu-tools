from django.conf.urls import patterns, include, url

urlpatterns = patterns('bambu.mail.views',
	url(r'^subscirbe/$', 'subscribe', name = 'newsletter_subscribe')
)