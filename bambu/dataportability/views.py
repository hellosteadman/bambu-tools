from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils import simplejson
from django.conf import settings
from django.http import Http404, HttpResponse
from mimetypes import guess_type
from bambu.dataportability.models import ImportJob, ExportJob

PUSHER_ENABLED = 'bambu.pusher' in settings.INSTALLED_APPS

@never_cache
@login_required
def status(request, guid, kind):
	if kind == 'import':
		job = get_object_or_404(ImportJob, guid = guid)
	elif kind == 'export':
		job = get_object_or_404(ExportJob, guid = guid)
	else:
		raise Http404('Job type not found.')
	
	if not request.is_ajax() and not job.updates.exists():
		job.start()
	
	updates = job.updates.all()
	if request.GET.get('latest'):
		try:
			latest = int(request.GET['latest'])
		except:
			latest = 0
		
		if latest > 0:
			updates = updates.filter(pk__gt = latest)
	
	if PUSHER_ENABLED:
		from bambu.pusher import enqueue
		enqueue.script(request)
	
	return TemplateResponse(
		request,
		request.is_ajax() and (
			'dataportability/%s-updates.inc.html' % kind)
		or (
			'dataportability/%s.html' % kind
		),
		{
			'job': job,
			'updates': updates,
			'latest_id': updates.exists() and updates.order_by('-pk')[0].pk or 0,
			'push_enabled': PUSHER_ENABLED
		}
	)

@never_cache
@login_required
def download(request, guid):
	job = get_object_or_404(ExportJob, guid = guid)
	mimetype, encoding = guess_type(job.name)
	
	resp = HttpResponse(
		job.data,
		mimetype = mimetype
	)
	
	resp['Content-Disposition'] = 'attachment; filename="%s"' % job.name
	return resp