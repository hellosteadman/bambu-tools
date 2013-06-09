from django.conf import settings

if 'bambu.saas' in settings.INSTALLED_APPS:
	from bambu.saas.signals import newsletter_optin
	from bambu.mail import receivers
	
	newsletter_optin.connect(receivers.newsletter_optin)