from django.db import transaction
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from bambu.webhooks.forms import ReceiverForm

@login_required
@permission_required('webhooks.change_webhook')
def webhooks(request):
	form = ReceiverForm(
		request.POST or None,
		user = request.user
	)
	
	if request.method == 'POST' and form.is_valid():
		with transaction.commit_on_success():
			form.save()
			
			messages.success(request, u'Your webhook settings have been saved successfully.')
			return HttpResponseRedirect(
				reverse('webhooks_manage')
			)
	
	return TemplateResponse(
		request,
		'webhooks/manage.html',
		{
			'form': form,
			'menu_selection': 'profile',
			'title_parts': ('Webhooks', 'My profile'),
			'breadcrumb_trail': (
				('../../', u'Home'),
				('../', u'My profile'),
				('', u'Webhooks')
			),
			'menu_selection': 'profile:webhooks'
		}
	)