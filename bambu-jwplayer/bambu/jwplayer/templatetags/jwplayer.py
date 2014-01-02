from django.template import Library
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import escape
from bambu.jwplayer import helpers
import random, string
register = Library()

@register.simple_tag()
def jwplayer(obj, field = 'video', ct = None):
	player_id = ''.join(random.sample(string.letters, 10))
	
	code = mark_safe(
		helpers.jwplayer_code(obj, field, player_id = player_id, ct = ct)
	)
	
	return code + mark_safe(
		render_to_string(
			'jwplayer/javascript.inc.html',
			{
				'id': player_id
			}
		)
	)

@register.simple_tag()
def jwplayer_ajax(obj, field = 'video', ct = None):
	from django.contrib.contenttypes.models import ContentType
	from django.db.models import Model
	from django.core.urlresolvers import reverse
	
	container = ''.join(random.sample(string.letters, 10))
	code = '<div id="%s"></div>' % container
	
	return mark_safe(
		code + render_to_string(
			'jwplayer/ajax.inc.html',
			{
				'id': container,
				'url': reverse(
					'jwplayer',
					args = [
						ct or ContentType.objects.get_for_model(obj).pk,
						isinstance(obj, dict) and obj.get('pk', 0) or getattr(obj, 'pk', 0),
						field
					]
				)
			}
		)
	)

@register.simple_tag()
def jwplayer_code(obj, field = 'video'):
	return escape(helpers.jwplayer_code(obj, field))