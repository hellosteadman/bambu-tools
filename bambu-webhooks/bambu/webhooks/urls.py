from django.conf.urls import patterns, url
from bambu.webhooks.views import webhooks
from django.conf import settings

if 'bambu.bootstrap' in settings.INSTALLED_APPS or 'bambu.bootstrap.v2' in settings.INSTALLED_APPS:
	from bambu.bootstrap.v2.decorators import body_classes
elif 'bambu.bootstrap.v3' in settings.INSTALLED_APPS:
	from bambu.bootstrap.v3.decorators import body_classes
else:
	def body_classes(view, *classes):
		return view

urlpatterns = patterns('',
	url(r'^$', body_classes(webhooks, 'profile', 'profile-edit', 'webhooks'), name = 'webhooks_manage'),
)