from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from bambu.notifications.models import Notification
from bambu.notifications.forms import NotificationsForm

@login_required
def manage(request):
	form = NotificationsForm(request.POST or None, user = request.user)
	if request.method == 'POST' and form.is_valid():
		with transaction.commit_on_success():
			form.save()
			messages.success(request, u'Your notification settings have been updated.')
			return HttpResponseRedirect('.')
	
	return TemplateResponse(
		request,
		'notifications/manage.html',
		{
			'form': form,
			'menu_selection': 'profile:notifications',
			'title_parts': ('Notification settings', 'My profile'),
			'breadcrumb_trail': (
				('../../', u'Home'),
				('../', u'My profile'),
				('', u'Notification settings')
			)
		}
	)

@login_required
def notification(request, pk):
	notification = get_object_or_404(Notification, pk = pk, relevant_to = request.user)
	return HttpResponse(notification.render_long())

@login_required
@transaction.commit_on_success
def delete_notification(request, pk):
	notification = get_object_or_404(Notification, pk = pk, relevant_to = request.user)
	notification.delete()
	
	return HttpResponse('OK')