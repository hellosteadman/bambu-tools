from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from bambu.preview.models import Preview

@never_cache
@login_required
def preview(request, pk):
	preview = get_object_or_404(Preview, pk = pk, creator = request.user)
	obj = preview.make_object()
	
	return TemplateResponse(
		request,
		(
			'preview/%s/%s.html' % (
				preview.content_type.app_label, preview.content_type.model
			),
			'preview/%s/object.html' % preview.content_type.app_label,
			'preview/object.html',
		),
		{
			'obj': obj,
			'content_type': preview.content_type,
			'body_classes': ('preview', 'preview-item'),
			'title_parts': (preview.title, u'Preview')
		}
	)