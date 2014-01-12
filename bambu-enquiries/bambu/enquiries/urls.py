from django.conf.urls import patterns, url
from bambu.enquiries.views import enquiry, enquiry_thanks
from django.conf import settings

if 'bambu.bootstrap' in settings.INSTALLED_APPS or 'bambu.bootstrap.v2' in settings.INSTALLED_APPS:
	from bambu.bootstrap.v2.decorators import body_classes
elif 'bambu.bootstrap.v3' in settings.INSTALLED_APPS:
	from bambu.bootstrap.v3.decorators import body_classes
else:
	def body_classes(view, *classes):
		return view

urlpatterns = patterns('',
	url(r'^$', body_classes(enquiry, 'enquiries'), name = 'enquiry'),
	url(r'^thanks/$', body_classes(enquiry_thanks, 'enquiries', 'enquiries-thanks'),
		name = 'enquiry_thanks'
	)
)