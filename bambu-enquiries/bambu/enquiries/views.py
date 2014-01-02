from django.template.response import TemplateResponse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import urlencode
from bambu.enquiries.models import Enquiry
from bambu.enquiries.forms import EnquiryForm

def enquiry(request):
	form = EnquiryForm(request.POST or None)
	
	if request.method == 'POST' and form.is_valid():
		enquiry = form.save(commit = False)
		spam = enquiry.check_for_spam(request)
		enquiry.save(notify = not spam)
		
		if 'bambu.analytics' in settings.INSTALLED_APPS:
			from bambu.analytics import track_event, events
			track_event(request, events.EVENT,
				category = u'Enquiry',
				action = u'Submit',
				option_label = enquiry.subject,
				option_value = enquiry.pk
			)
		
		return HttpResponseRedirect(
			'thanks/?%s' % urlencode(
				{
					'next': request.GET.get('next', '/')
				}
			)
		)
	
	return TemplateResponse(
		request,
		'enquiries/enquiry.html',
		{
			'form': form,
			'menu_selection': 'enquiry',
			'next': request.GET.get('next', '/')
		}
	)
	
def enquiry_thanks(request):
	return TemplateResponse(
		request,
		'enquiries/thanks.html',
		{
			'next': request.GET.get('next', '/')
		}
	)