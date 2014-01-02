from django.conf.urls import patterns, url
from bambu.webhooks.views import webhooks

try:
	from bambu.bootstrap.decorators import body_classes
	urlpatterns = patterns('',
		url(r'^$', body_classes(webhooks, 'profile', 'profile-edit', 'webhooks'), name = 'webhooks_manage'),
	)
except ImportError:
	urlpatterns = patterns('',
		url(r'^$', webhooks, name = 'webhooks_manage'),
	)