from django.conf.urls import patterns, url
from bambu.notifications.views import manage
from django.conf import settings

if 'bambu.bootstrap' in settings.INSTALLED_APPS or 'bambu.bootstrap.v2' in settings.INSTALLED_APPS:
	from bambu.bootstrap.v2.decorators import body_classes
elif 'bambu.bootstrap.v3' in settings.INSTALLED_APPS:
	from bambu.bootstrap.v3.decorators import body_classes
else:
	def body_classes(view, *classes):
		return view

urlpatterns = patterns('bambu.notifications.views',
	url(r'^$', body_classes(manage, 'profile', 'profile-edit', 'notifications'), name = 'notifications_manage'),
	url(r'^(?P<pk>\d+)/$', 'notification', name = 'notification'),
	url(r'^(?P<pk>\d+)/delete/$', 'delete_notification', name = 'delete_notification')
)