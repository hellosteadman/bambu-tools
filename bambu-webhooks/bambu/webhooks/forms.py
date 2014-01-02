from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from bambu.webhooks.models import Receiver
from bambu.webhooks import site

class ReceiverForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		hooks = {}
		
		for (hook, url) in self.user.webhooks.values_list('hook', 'url'):
			hooks[hook] = hooks.get(hook, []) + [url]
		
		kwargs['initial'] = dict(
			[
				(h, '\n'.join(u)) for (h, u) in hooks.items()
			]
		)
		
		super(ReceiverForm, self).__init__(*args, **kwargs)
		
		for name, hook in site._registry.items():
			if hook.get('staff_only') and not self.user.is_staff:
				continue
			
			self.fields[name] = forms.CharField(
				widget = forms.Textarea(
					attrs = {
						'rows': 3
					}
				),
				label = hook.get('verbose_name', name).capitalize(),
				help_text = hook.get('description'),
				required = False
			)
			
			setattr(self, 'clean_%s' % name, self.clean_FIELD(name))
	
	def clean_FIELD(self, name):
		def inner():
			data = self.cleaned_data.get(name, '')
			validate = URLValidator()
			
			for i, url in enumerate([u.strip() for u in data.splitlines()]):
				try:
					validate(url)
				except ValidationError:
					raise forms.ValidationError(
						u'Line %d contains an invalid URL' % (i + 1)
					)
			
			return data
		
		return inner
	
	def save(self):
		hooks = site._registry.keys()
		for name in hooks:
			urls = [u.strip() for u in self.cleaned_data.get(name, '').splitlines()]
			
			for url in urls:
				if not self.user.webhooks.filter(
					hook = name,
					url = url
				).exists():
					self.user.webhooks.create(
						hook = name,
						url = url
					)
			
			self.user.webhooks.filter(
				hook = name
			).exclude(
				url__in = urls
			).delete()
		
		self.user.webhooks.exclude(hook__in = hooks).delete()