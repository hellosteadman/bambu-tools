from django.conf.urls import patterns, include, url
from bambu.bootstrap.decorators import body_classes
from bambu.faq.views import topics

urlpatterns = patterns('',
	url(r'^$', body_classes(topics, 'faq'), name = 'faq_topics'),
	url(r'^(?P<category>[\w-]+)/$', body_classes(topics, 'faq', 'faq-category'),
		name = 'faq_topics_category'
	)
)