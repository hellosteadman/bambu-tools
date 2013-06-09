from django.conf import settings
from django.utils import simplejson
from django.utils.http import urlencode
from urllib2 import Request, urlopen, HTTPError
from elementtree import ElementTree
import re

URL_REGEX = re.compile(
    r'<p>(?P<url>(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+))<\/p>', re.IGNORECASE
)

URL_PATTERNS = (
	(r'^https?://(?:.+\.)?blip\.tv/file/.+$', 'http://blip.tv/oembed/?%s', 'json'),
	(r'^https?://(?:www\.)?clikthrough\.com/theater/.+$', 
		'http://clikthrough.com/services/oembed/?%s', 'json'
	),
	(r'^https?://(?:www\.)?dailymotion\.com/video/.+$',
		'http://www.dailymotion.com/api/oembed/?%s', 'json'
	),
	(r'^https?://(?:www\.)?dotsub\.com/view/.+$',
		'http://dotsub.com/services/oembed?%s', 'json'
	),
	(r'^https?://(?:www\.)?flickr\.com/photos/.+$',
		'http://www.flickr.com/services/oembed/?%s', 'xml'
	),
	(r'^https?://(?:www\.)?hulu\.com/watch/.+$',
		'http://www.hulu.com/api/oembed.json?%s', 'json'
	),
	(r'^https?://(?:www\.)?kinomap\.com/.+$',
		'http://www.kinomap.com/oembed?%s', 'xml'
	),
	(r'^https?://(?:www\.)?nfb\.ca/film/.+$',
		'http://www.nfb.ca/remote/services/oembed/?%s',
		'xml'
	),
	(r'^https?://(?:www\.)?poddle\.tv/[\w-]+/\d+/$',
		'http://poddle.tv/oembed/?%s', 'json'
	),
	(r'^https?://(.+\.)?photobucket\.com/(?:albums|groups)/.+$', 
		'http://photobucket.com/oembed?%s', 'json'
	),
	(r'^https?://(?:www\.)?qik\.com/video/.+$',
		'http://qik.com/api/oembed.json?%s', 'json'
	),
	(r'^https?://(?:www\.)?revision3\.com/.+$',
		'http://revision3.com/api/oembed/?%s', 'json'
	),
	(r'^https?://(?:www\.)?scribd\.com/doc/.+$',
		'http://www.scribd.com/services/oembed?%s', 'json'
	),
	(r'^https?://(?:www\.)?twitter\.com/(?:#!/)?[\w]+/status/\d+/?$',
		'https://api.twitter.com/1/statuses/oembed.json?%s', 'json'
	),
	(r'^https?://(?:www\.)?viddler\.com/v/.+$',
		'http://www.viddler.com/oembed/?%s&format=json', 'json'
	),
	(r'^https?://(?:www\.)?vimeo\.com/.+$',
		'http://vimeo.com/api/oembed.json?%s', 'json'
	),
	(r'^https?://(?:www\.)?yfrog\.(?:com|ru|com\.tr|it|fr|co\.il|co\.uk|com\.pl|pl|eu|us)/.+$', 
		'http://www.yfrog.com/api/oembed?%s', 'json'
	),
	(r'^https?://(?:www\.)?youtube\.com/watch\?v=.+$',
		'http://www.youtube.com/oembed?%s', 'json'
	),
	(r'^https?://(?:www\.)?youtu\.be/.+$',
		'http://www.youtube.com/oembed?%s', 'json'
	)
)

def get_oembed_response(url, endpoint, format, width = None):
	if not width:
		width = getattr(settings, 'OEMBED_WIDTH', 640)
	
	if format == 'json':
		mimetype = 'application/json'
	elif format == 'xml':
		mimetype = 'text/xml'
	elif format != 'html':
		raise Exception('Handler configured incorrectly (unrecognised format %s)' % format)
	
	params = {
		'url': url
	}
	
	if int(width) > 0:
		params['width'] = width
		params['maxwidth'] = width
	
	if not callable(endpoint):
		oembed_request = Request(
			endpoint % urlencode(params),
			headers = {
				'Accept': mimetype,
				'User-Agent': 'bambu-tools/2.1'
			}
		)
		
		try:
			return urlopen(oembed_request)
		except HTTPError, ex:
			raise Exception(ex.msg)
	else:
		return endpoint(url)

def get_oembed_content(url, endpoint, format, width = None):
	response = get_oembed_response(url, endpoint, format, width)
	
	if format == 'json':
		try:
			json = simplejson.load(response)
		except:
			raise Exception('Not a JSON response')
		
		if 'html' in json:
			return json.get('html')
		elif 'thumbnail_url' in json:
			return '<a href="%(resource)s"><img alt=="%(title)s" src="%(url)s" /></a>' % {
				'title': json['title'],
				'url': json['thumbnail_url'],
				'resource': url,
			}
		else:
			raise Exception('Response not understood', json)
	else:
		try:
			xml = ElementTree.parse(response)
		except:
			raise Exception('Not an XML response')
		
		try:
			return xml.getroot().find('html').text or ''
		except:
			if not xml.find('url') is None:
				return '<a href="%(resource)s"><img alt=="%(title)s" src="%(url)s" /></a>' % {
					'title': xml.find('title') and xml.find('title').text or '',
					'url': xml.find('url').text,
					'resource': url
				}
			else:
				raise Exception('No embeddable content found')