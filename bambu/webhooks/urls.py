from django.conf.urls import patterns, url
from bambu.bootstrap.decorators import body_classes
from bambu.webhooks.views import webhooks

urlpatterns = patterns('',
	url(r'^$', body_classes(webhooks, 'profile', 'profile-edit', 'webhooks'), name = 'webhooks_manage'),
)