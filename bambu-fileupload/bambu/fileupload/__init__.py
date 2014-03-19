from django.core.files import File

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

def get_ajax_uploads(request):
	from bambu.fileupload.models import FileUploadContext
	guid = request.POST.get('_bambu_fileupload_guid')

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

def clear_ajax_uploads(request):
	from bambu.fileupload.models import FileUploadContext
	guid = request.POST.get('_bambu_fileupload_guid')

	if guid:
		try:
			context = FileUploadContext.objects.get(uuid = guid)
		except FileUploadContext.DoesNotExist:
			return

		context.attachments.all().delete()

def ajax_upload_count(request):
	from bambu.fileupload.models import FileUploadContext
	guid = request.POST.get('_bambu_fileupload_guid')

	if guid:
		try:
			context = FileUploadContext.objects.get(uuid = guid)
		except FileUploadContext.DoesNotExist:
			return 0

		return context.attachments.count()
