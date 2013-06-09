from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import HttpResponseRedirect
from bambu.mail import shortcuts

def subscribe(request):
	email = request.POST.get('email')
	next = request.POST.get('next', request.GET.get('next', '/'))
	valid = False
	
	if not email:
		messages.error(request, u'Please enter your email address')
	else:
		try:
			validate_email(email)
			valid = True
		except ValidationError:
			messages.error(request, u'Please enter a valid email address')
	
	if valid:
		shortcuts.subscribe(email, list_id = 'newsletter')
		messages.success(request, u'Thanks for subscribing to our newsletter.')
	
	return HttpResponseRedirect(next)