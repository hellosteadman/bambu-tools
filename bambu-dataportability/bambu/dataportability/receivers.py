def pre_import_delete(sender, instance, **kwargs):
	instance.data.delete()

def pre_export_delete(sender, instance, **kwargs):
	if instance.data:
		instance.data.delete()