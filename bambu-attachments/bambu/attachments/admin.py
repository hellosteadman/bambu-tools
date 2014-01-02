from django.contrib.contenttypes import generic
from bambu.attachments.models import Attachment
from bambu.attachments.forms import AttachmentForm

class AttachmentInline(generic.GenericStackedInline):
	model = Attachment
	extra = 0
	form = AttachmentForm