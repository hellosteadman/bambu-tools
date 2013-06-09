from django.conf.urls import patterns, include, url

urlpatterns = patterns('bambu.payments.views',
	url(r'^(?P<payment>\d+)/cancel/$', 'cancel', name = 'payment_cancel'),
	url(r'^(?P<payment>\d+)/callback/$', 'callback', name = 'payment_callback'),
	url(r'^(?P<gateway>[\w-]+)/callback/$', 'callback', name = 'payment_callback_generic')
)