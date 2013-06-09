from bambu.minidetect import SEARCH_STRINGS_FILENAME, _thread_locals
from django.conf import settings
from os import path

SEARCH_STRINGS = []
TEMPLATE_DIRS = settings.TEMPLATE_DIRS

for l in open(SEARCH_STRINGS_FILENAME, 'r').read().splitlines():
	if not l.startswith('#'):
		SEARCH_STRINGS.append(l.strip())

class MiniDetectMiddleware(object):
	def process_request(self, request):
		useragent = request.META.get('HTTP_USER_AGENT', '').lower()
		request.mobile = False
		
		for ss in SEARCH_STRINGS:
			if ss in useragent:
				request.mobile = True
				break
		
		_thread_locals.request = request