from django.conf.urls import url, patterns
from bambu.xmlrpc import autodiscover

autodiscover()

urlpatterns = patterns('bambu.xmlrpc.views',
	url(r'^xml-rpc/$', 'dispatch', name = 'xmlrpc_server')
)