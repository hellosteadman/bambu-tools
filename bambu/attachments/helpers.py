from os import path
from django.utils.timezone import utc
from datetime import datetime
from uuid import uuid4

def upload_attachment_file(instance, filename):
	return 'attachments/%s/%s%s' % (
		datetime.utcnow().replace(tzinfo = utc).strftime('%Y/%m'),
		str(uuid4()),
		path.splitext(filename)[-1]
	)