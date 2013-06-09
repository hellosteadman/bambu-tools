from django.template.response import TemplateResponse
from django.conf import settings
from django.http import HttpResponseRedirect
from bambu.enquiries.models import Enquiry
from bambu.enquiries.forms import EnquiryForm

def enquiry(request):
	form = EnquiryForm(request.POST or None)
	
	if request.method == 'POST' and form.is_valid():
		enquiry = form.save()
		
		if 'bambu.analytics' in settings.INSTALLED_APPS:
			from bambu.analytics import track_event, events
			track_event(request, events.EVENT,
				category = u'Enquiry',
				action = u'Submit',
				option_label = enquiry.subject,
				option_value = enquiry.pk
			)
		
		return HttpResponseRedirect('thanks/')
	
	return TemplateResponse(
		request,
		'enquiries/enquiry.html',
		{
			'form': form,
			'menu_selection': 'enquiry'
		}
	)
	
def enquiry_thanks(request):
	return TemplateResponse(
		request,
		'enquiries/thanks.html',
		{}
	)