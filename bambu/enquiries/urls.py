from django.conf.urls import patterns, url
from bambu.bootstrap.decorators import body_classes
from bambu.enquiries.views import enquiry, enquiry_thanks

urlpatterns = patterns('',
	url(r'^$', body_classes(enquiry, 'enquiries'), name = 'enquiry'),
	url(r'^thanks/$', body_classes(enquiry_thanks, 'enquiries', 'enquiries-thanks'),
		name = 'enquiry_thanks'
	)
)