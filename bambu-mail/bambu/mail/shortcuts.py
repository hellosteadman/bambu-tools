from bambu.mail.tasks import render_to_mail_task
from django.conf import settings
from django.utils.importlib import import_module

def render_to_mail(subject, template, context, recipient, fail_silently = False):
	if 'djcelery' in settings.INSTALLED_APPS:
		render_to_mail_task.delay(
			subject,
			template,
			context,
			recipient,
			fail_silently
		)
	else:
		render_to_mail_task(
			subject,
			template,
			context,
			recipient,
			fail_silently
		)

def subscribe(email, **kwargs):
	provider = getattr(settings, 'NEWSLETTER_PROVIDER')
	module, dot, klass = provider.rpartition('.')
	ps = getattr(settings,
		'NEWSLETTER_SETTINGS', {
			klass: {}
		}
	).get(klass)
	
	module = import_module(module)
	klass = getattr(module, klass)
	provider = klass(**ps)
	return provider.subscribe(email, **kwargs)