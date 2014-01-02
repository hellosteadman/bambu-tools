from bambu.minidetect.mdetect import UAgentInfo

class MiniDetectMiddleware(object):
	def process_request(self, request):
		useragent = request.META.get('HTTP_USER_AGENT', '').lower()
		accept = request.META.get('HTTP_ACCEPT', '').lower()
		request.mobile = False
		request.formfactor = 'unknown'
		
		if useragent:
			useragent = UAgentInfo(useragent, accept)
			is_tablet = useragent.detectTierTablet()
			is_phone = useragent.detectTierIphone()
			is_mobile = is_tablet or is_phone or useragent.detectMobileQuick()
			
			if is_mobile:
				request.mobile = True
				request.formfactor = is_tablet and 'tablet' or is_phone and 'handheld' or 'unknown'