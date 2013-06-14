from django.db.models import Model, DateField, DateTimeField, ManyToManyField, FileField
from django.db.models.query import QuerySet
from django.db.models.fields.related import ForeignKey
from django.core.files import File
from django.conf import settings
from django.utils.timezone import get_current_timezone
from datetime import date, datetime, time
from uuid import uuid4
from os import path

def get_serialisable_fields(obj):
	opts = obj._meta
	fields = (field.name for field in opts.local_fields + opts.local_many_to_many)
	fields = (opts.get_field(field) for field in fields)
	
	for field in fields:
		if field.rel:
			yield field.name
		else:
			yield field.attname

def upload_attachment_file(instance, filename):
	return 'preview/%s/%s/%s' % (
		instance.preview.content_type.app_label,
		instance.preview.content_type.model,
		path.split(filename)[-1]
	)

def serialise(value):
	if isinstance(value, Model):
		return value.pk
	elif isinstance(value, datetime):
		return value.strftime('%Y-%m-%d %H:%M:%S')
	elif isinstance(value, date):
		return value.strftime('%Y-%m-%d')
	elif isinstance(value, time):
		return value.strftime('%H:%M:%S')
	elif isinstance(value, QuerySet):
		return [v for v in value.values_list('pk', flat = True)]
	elif isinstance(value, File):
		return None
	else:
		return value

def unserialise(field, value):
	if isinstance(field, ForeignKey):
		return field.rel.to.objects.get(pk = value)
	elif isinstance(field, DateTimeField):
		return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(tzinfo = get_current_timezone())
	elif isinstance(field, DateField):
		return datetime.strptime(value, '%Y-%m-%d').replace(tzinfo = get_current_timezone())
	elif isinstance(field, ManyToManyField):
		return field.rel.to.objects.filter(pk__in = value)
	elif isinstance(field, FileField):
		if value.startswith(settings.MEDIA_URL):
			return value[len(settings.MEDIA_URL):]
		else:
			return value
	else:
		return value