from bambu.saas.models import UserPlan

class UserPlanMiddleware(object):
	def process_request(self, request, *args, **kwargs):
		user = getattr(request, 'user', None)
		if not user:
			return
		
		if user.is_anonymous():
			return
		
		def getplan():
			if not hasattr(request, '_userplan'):
				try:
					request._userplan = UserPlan.objects.get_for_user(user)
				except UserPlan.DoesNotExist:
					request._userplan = None
			
			return request._userplan
		
		request.plan = getplan