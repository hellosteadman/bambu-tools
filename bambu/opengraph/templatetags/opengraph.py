from django.template import Library
from django.conf import settings
from django.contrib.sites.models import Site

register = Library()

@register.inclusion_tag('opengraph/meta.inc.html', takes_context = True)
def opengraph_meta_tags(context):
	request = context.get('request')
	site = context.get('SITE') or Site.objects.get_current()
	
	meta = {
		'title': ' | '.join(context.get('title_parts', ())),
		'url': (request and site) and 'http://%s%s' % (site.domain, request.path) or '',
		'site_name': site.name or site.domain,
		'type': 'article'
	}
	
	meta.update(context.get('og_meta', {}))
	return {
		'app_id': getattr(settings, 'FACEBOOK_APP_ID', ''),
		'values': meta.items()
	}