from bambu.webhooks import site

def get_hook_choices():
	return [(k, v['verbose_name']) for k, v in site._registry.items()]