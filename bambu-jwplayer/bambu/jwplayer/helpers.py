from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.http import urlencode

def get_plugins(obj, domain):
	plugins = {}
	
	for key, options in getattr(settings, 'JWPLAYER_PLUGINS', {}).items():
		plugin = {}
		
		for subkey, option in options.items():
			plugin[subkey] = option % {
				'link': '//%s%s' % (domain, obj.get_absolute_url()),
				'embed': jwplayer_code(obj)
			}
			
		plugins[key] = plugin
	
	return plugins

def jwplayer_url(obj, field = 'video'):
	return reverse(
		'jwplayer',
		args = [ContentType.objects.get_for_model(obj).pk, obj.pk, field]
	)

def jwplayer_swf_url(obj, field = 'video', width = 640, height = 320, static_url = None):
	ct = ContentType.objects.get_for_model(obj)
	streamer = getattr(settings, 'JWPLAYER_STREAMER', None)
	site = Site.objects.get_current()
	
	if not static_url:
		static_url = settings.STATIC_URL
		if not static_url.startswith('http://') and not static_url.startswith('https://'):
			static_url = '//%s%s' % (site.domain, static_url)
	
	try:
		width = int(width)
	except:
		width = settings.VIDEO_WIDTH
	
	height = int(float(width) / 16.0 * 9.0)
	video = getattr(obj, field, None)
	
	if not video:
		return None
	
	thumbnail = getattr(obj, 'thumbnail', None)
	if thumbnail:
		thumbnail = thumbnail.url
	
	video_url = video.url
	base = video_url[:video_url.find('/', 8) + 1]
	video_name = video_url[len(base):]
	
	kwargs = {
		'file': streamer and video_name or video_url,
		'skin': '%sjwplayer/skins/bekle.zip' % static_url,
		'flashplayer': '%sjwplayer/player.swf' % static_url,
		'controlbar.position': 'over'
	}
	
	if thumbnail:
		kwargs['image'] = thumbnail
	
	if streamer:
		kwargs.update(
			{
				'provider': 'rtmp',
				'streamer': streamer
			}
		)
	
	return '%sjwplayer/player.swf?%s' % (
		static_url, urlencode(kwargs)
	)

def jwplayer_code(obj, field = 'video', **kwargs):
	site = Site.objects.get_current()
	width = int(kwargs.get('width') or settings.VIDEO_WIDTH)
	
	if hasattr(settings, 'MAX_VIDEO_WIDTH'):
		if width > settings.MAX_VIDEO_WIDTH:
			width = settings.MAX_VIDEO_WIDTH
	
	height = float(width) / 16.0 * 9.0
	player_id = kwargs.get('player_id', None) and (' id="%s"' % kwargs['player_id']) or ''
	ctpk = kwargs.get('ct') or ContentType.objects.get_for_model(obj).pk
	
	return u'<iframe%(id)s width="%(width)d" height="%(height)d" ' \
		u'src="//%(domain)s%(url)s?width=%(width)d" ' \
		u'style="border-width:0;overflow:hidden;" frameborder="0"></iframe>' % {
			'id': player_id,
			'width': width,
			'height': height,
			'domain': site.domain,
			'url': reverse(
				'jwplayer',
				args = [
					ctpk,
					isinstance(obj, dict) and obj.get('pk', 0) or getattr(obj, 'pk', 0),
					field
				]
			)
		}