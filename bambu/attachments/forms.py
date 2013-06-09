from django import forms
from bambu.attachments.models import Attachment

class AttachmentForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(AttachmentForm, self).__init__(*args, **kwargs)
		self.fields['title'].required = False
	
	class Meta:
		model = Attachment