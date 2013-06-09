from django.conf.urls import patterns, url

urlpatterns = patterns('bambu.mapping.views',
	url(r'^functions\.js$', 'functions_js', name = 'bambu_mapping_functions')
)