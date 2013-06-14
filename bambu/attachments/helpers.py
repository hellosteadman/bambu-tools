from os import path
from django.utils.timezone import now
from uuid import uuid4

def upload_attachment_file(instance, filename):
	return 'attachments/%s/%s%s' % (
		now().strftime('%Y/%m'),
		str(uuid4()),
		path.splitext(filename)[-1]
	)