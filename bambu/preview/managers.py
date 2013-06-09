from django.db.models import Manager
from django.core.files import File
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from bambu.preview.helpers import *
from uuid import uuid4
from os import path

class PreviewManager(Manager):
	def clear_for_model(self, obj, user):
		self.model.objects.filter(
			content_type = ContentType.objects.get_for_model(obj),
			creator = user
		).delete()
	
	def create_preview(self, model, title, data, user, inline_data = []):
		from django.utils import simplejson
		
		fields = get_serialisable_fields(model)
		save = {}
		files = []
		
		for field in fields:
			if field in data:
				value = serialise(data[field])
				if value:
					save[field] = value
		
		if any(inline_data):
			inlines = {}
			
			for (submodel, data_list) in inline_data:
				key = '%s.%s' % (submodel._meta.app_label, submodel._meta.module_name)
				inline_list = inlines.get(key, [])
				
				for data_item in data_list:
					data_dict = {}
					fields = get_serialisable_fields(submodel)
					
					for field in fields:
						if field in data_item:
							value = serialise(data_item[field])
							if isinstance(data_item[field], File):
								filename = 'preview/%s/%s/%s%s' % (
									model._meta.app_label,
									model._meta.module_name,
									str(uuid4()),
									path.splitext(data_item[field].name)[-1]
								)
								
								files.append(
									File(
										data_item[field],
										name = filename
									)
								)
								
								data_dict[field] = settings.MEDIA_URL + filename
							elif value:
								data_dict[field] = value
					
					inline_list.append(data_dict)
				
				inlines[key] = inline_list
			
			save['_inlines'] = inlines
		
		obj = self.model(
			content_type = ContentType.objects.get_for_model(model),
			title = title,
			creator = user,
			data = simplejson.dumps(save)
		)
		
		obj.save()
		for f in files:
			obj.attachments.create(file = f)
		
		return obj