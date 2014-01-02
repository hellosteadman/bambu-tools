from django.http import HttpResponse, HttpResponseRedirect
from django.utils.http import urlencode
from bambu.saas.models import UserPlan, Feature
from django.core.urlresolvers import reverse

def feature_required(feature, redirect_url = '/upgrade/', **kw):
	def _dec(view_func):
		def _view(request, *args, **kwargs):
			def _redirect(url):
				if request.is_ajax():
					return HttpResponse('::301::' + url)
				else:
					return HttpResponseRedirect(url)
			
			if request.user.is_authenticated():
				for k, v in kw.items():
					if callable(v):
						kw[k] = v(*args, **kwargs)
				
				plan = getattr(request, 'plan', None)
				if plan:
					plan = plan()
				
				if not plan:
					try:
						plan = UserPlan.objects.get_for_user(request.user)
					except UserPlan.DoesNotExist:
						return _redirect('%s?feature=%s' % (redirect_url, feature))
				
				if plan.has_feature(feature, **kw):
					return view_func(request, *args, **kwargs)
				
				return _redirect('%s?feature=%s' % (redirect_url, feature))
			
			return _redirect(
				'%s?%s' % (
					reverse('signup'),
					urlencode(
						{
							'next': request.path
						}
					)
				)
			)
		
		return _view
	
	return _dec