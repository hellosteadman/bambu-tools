from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.conf import settings
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils.http import urlencode
from django.conf import settings
from bambu.jwplayer.helpers import get_plugins

def player(request, content_type, object_id, field):
	ct = get_object_or_404(ContentType, pk = content_type)
	obj = get_object_or_404(ct.model_class(), pk = object_id)
	site = Site.objects.get_current()
	width = request.GET.get('width', getattr(settings, 'VIDEO_WIDTH', 640))
	streamer = getattr(settings, 'JWPLAYER_STREAMER', None)
	
	try:
		width = int(width)
	except:
		width = getattr(settings, 'VIDEO_WIDTH', 640)
	
	height = int(float(width) / 16.0 * 9.0)
	video = getattr(obj, field, None)
	
	if not video:
		return TemplateResponse(
			request,
			'jwplayer/404.html',
			{}
		)
	
	thumbnail = getattr(obj, 'thumbnail', None)
	if thumbnail:
		thumbnail = thumbnail.url
	
	video_url = video.url
	if video_url.startswith('//'):
		video_url = 'http:%s' % video_url
	elif video_url.startswith('/'):
		video_url = 'http://%s%s' % (site.domain, video_url)
	
	base = video_url[:video_url.find('/', 8) + 1]
	video_name = video_url[len(base):]
	
	chapters = []
	if hasattr(obj, 'chapters'):
		for chapter in obj.chapters.all():
			parts = chapter.timecode.split(':')
			if len(parts) == 3:
				minutes, seconds, milliseconds = parts
			elif len(parts) == 2:
				minutes, seconds = parts
				milliseconds = 0
			else:
				minutes = parts[0]
				seconds, milliseconds = 0, 0
			
			minutes, seconds, milliseconds = int(minutes), int(seconds), int(milliseconds)
			milliseconds += (seconds * 1000) + (minutes * 60000)
			
			chapters.append(
				(milliseconds, chapter.name)
			)
	
	return TemplateResponse(
		request,
		'jwplayer/player.html',
		{
			'video_url': video_url,
			'video_name': streamer and video_name or video_url,
			'streamer': streamer,
			'thumbnail': thumbnail,
			'width': width,
			'height': height,
			'name': unicode(obj),
			'STATIC_SECURE_URL': getattr(settings, 'STATIC_SECURE_URL', settings.STATIC_URL),
			'plugins': get_plugins(obj, site.domain),
			'chapters': chapters
		}
	)