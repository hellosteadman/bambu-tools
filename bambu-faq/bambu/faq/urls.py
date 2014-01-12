from django.conf.urls import patterns, include, url
from bambu.faq.views import topics
from django.conf import settings

if 'bambu.bootstrap' in settings.INSTALLED_APPS or 'bambu.bootstrap.v2' in settings.INSTALLED_APPS:
	from bambu.bootstrap.v2.decorators import body_classes
elif 'bambu.bootstrap.v3' in settings.INSTALLED_APPS:
	from bambu.bootstrap.v3.decorators import body_classes
else:
	def body_classes(view, *classes):
		return view

urlpatterns = patterns('',
	url(r'^$', body_classes(topics, 'faq'), name = 'faq_topics'),
	url(r'^(?P<category>[\w-]+)/$', body_classes(topics, 'faq', 'faq-category'),
		name = 'faq_topics_category'
	)
)