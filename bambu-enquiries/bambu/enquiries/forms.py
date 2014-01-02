from django import forms
from django.conf import settings
from bambu.enquiries.models import Enquiry

try:
	from bambu.comments.helpers import sanitise
except ImportError:
	def sanitise(text, *args):
		return text

MARKDOWN = getattr(settings, 'COMMENTS_MARKDOWN', True)

class EnquiryForm(forms.ModelForm):
	def save(self, commit = True):
		obj = super(EnquiryForm, self).save(commit = False)
		obj.message = sanitise(self.cleaned_data['message'], MARKDOWN)
		
		if commit:
			obj.save()
		
		return obj
	
	class Meta:
		model = Enquiry
		fields = ('name', 'email', 'subject', 'message')