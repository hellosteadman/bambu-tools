from django.core.files import File
from django.http import HttpRequest

__version__ = '0.3'

DEFAULT_HANDLERS = (
	(
		'attachments',
		(
			'bambu.fileupload.handlers.upload_attachment',
			'bambu.fileupload.addAttachment',
			'bambu.fileupload.handlers.delete_attachment',
			'bambu.fileupload.handlers.get_attachments'
		)
	),
)

class FileUploadError(Exception):
	pass

def get_ajax_uploads(request_or_guid):
	from bambu.fileupload.models import FileUploadContext
	if isinstance(request_or_guid, (str, unicode)):
		guid = request_or_guid
	elif isinstance(request_or_guid, HttpRequest):
		guid = request_or_guid.POST.get('_bambu_fileupload_guid')
	else:
		raise TypeError(
			'Argument must be an HttpRequest object or a string ' \
			'containing a file-upload context'
		)

	if guid:
		context = FileUploadContext.objects.get(uuid = guid)
		for a in context.attachments.all():
			yield (
				a,
				File(
					a.file,
					name = a.file.name
				),
				a.file.size
			)

def clear_ajax_uploads(request_or_guid):
	from bambu.fileupload.models import FileUploadContext
	if isinstance(request_or_guid, (str, unicode)):
		guid = request_or_guid
	elif isinstance(request_or_guid, HttpRequest):
		guid = request_or_guid.POST.get('_bambu_fileupload_guid')
	else:
		raise TypeError(
			'Argument must be an HttpRequest object or a string ' \
			'containing a file-upload context'
		)

	if guid:
		try:
			context = FileUploadContext.objects.get(uuid = guid)
		except FileUploadContext.DoesNotExist:
			return

		context.attachments.all().delete()

def ajax_upload_count(request_or_guid):
	from bambu.fileupload.models import FileUploadContext
	if isinstance(request_or_guid, (str, unicode)):
		guid = request_or_guid
	elif isinstance(request_or_guid, HttpRequest):
		guid = request_or_guid.POST.get('_bambu_fileupload_guid')
	else:
		raise TypeError(
			'Argument must be an HttpRequest object or a string ' \
			'containing a file-upload context'
		)

	if guid:
		try:
			context = FileUploadContext.objects.get(uuid = guid)
		except FileUploadContext.DoesNotExist:
			return 0

		return context.attachments.count()
