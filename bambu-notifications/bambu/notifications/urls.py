from django.conf.urls import patterns, url
from bambu.notifications.views import manage

try:
	from bambu.bootstrap.decorators import body_classes
	urlpatterns = patterns('bambu.notifications.views',
		url(r'^$', body_classes(manage, 'profile', 'profile-edit', 'notifications'), name = 'notifications_manage'),
		url(r'^(?P<pk>\d+)/$', 'notification', name = 'notification'),
		url(r'^(?P<pk>\d+)/delete/$', 'delete_notification', name = 'delete_notification')
	)
except ImportError:
	urlpatterns = patterns('bambu.notifications.views',
		url(r'^$', manage, name = 'notifications_manage'),
		url(r'^(?P<pk>\d+)/$', 'notification', name = 'notification'),
		url(r'^(?P<pk>\d+)/delete/$', 'delete_notification', name = 'delete_notification')
	)