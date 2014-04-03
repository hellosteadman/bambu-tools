from django.db import transaction
from django.core.files import File
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from bambu.fileupload.models import FileUploadContext
from bambu.attachments import MIMETYPES
from bambu.attachments.models import Attachment
from tempfile import mkstemp
from mimetypes import guess_type
import os

@transaction.commit_on_success()
def upload_attachment(request, file, *args, **kwargs):
	context, created = FileUploadContext.objects.select_for_update().get_or_create(
		uuid = u''.join(kwargs['guid']),
		user = request.user
	)

	handle, dest = mkstemp(
		suffix = os.path.splitext(file.name)[-1]
	)

	try:
		os.write(handle, file.read())
	finally:
		os.close(handle)

	mimetype, encoding = guess_type(dest)
	if not mimetype in MIMETYPES:
		return False

	try:
		return Attachment.objects.select_for_update().create(
			content_type = ContentType.objects.get_for_model(FileUploadContext),
			object_id = context.pk,
			file = File(
				open(dest, 'rb')
			)
		).file.url
	finally:
		os.remove(dest)

@transaction.commit_on_success()
def delete_attachment(request, filename, *args, **kwargs):
	context = FileUploadContext.objects.select_for_update().get(
		uuid = request.GET.get('guid'),
		user = request.user
	)

	if filename.startswith(settings.MEDIA_URL):
		filename = filename[len(settings.MEDIA_URL):]

	return context.attachments.filter(file = filename).delete()

def get_attachments(request, *args, **kwargs):
	try:
		context = FileUploadContext.objects.get(
			uuid = request.GET.get('guid'),
			user = request.user
		)
	except FileUploadContext.DoesNotExist:
		return []

	return [
		{
			'name': attachment.file.name,
			'size': attachment.size,
			'url': attachment.file.url,
 			'type': attachment.mimetype
		} for attachment in context.attachments.all()
	]
