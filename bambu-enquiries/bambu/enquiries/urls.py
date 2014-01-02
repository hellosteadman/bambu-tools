from django.conf.urls import patterns, url
from bambu.enquiries.views import enquiry, enquiry_thanks

try:
	from bambu.bootstrap.decorators import body_classes
	urlpatterns = patterns('',
		url(r'^$', body_classes(enquiry, 'enquiries'), name = 'enquiry'),
		url(r'^thanks/$', body_classes(enquiry_thanks, 'enquiries', 'enquiries-thanks'),
			name = 'enquiry_thanks'
		)
	)
except ImportError:
	urlpatterns = patterns('',
		url(r'^$', enquiry, name = 'enquiry'),
		url(r'^thanks/$', enquiry_thanks, name = 'enquiry_thanks')
	)