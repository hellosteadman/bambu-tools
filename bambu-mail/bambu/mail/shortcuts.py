from bambu.mail.tasks import render_to_mail_task, subscribe_task
from django.conf import settings

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
	if 'djcelery' in settings.INSTALLED_APPS:
		subscribe_task.delay(
			email,
			**kwargs
		)
	else:
		subscribe_task(
			email,
			**kwargs
		)