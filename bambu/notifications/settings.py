from django.conf import settings as site_settings

DEFAULT_DELIVERY_METHODS = getattr(site_settings, 'NOTIFICATIONS_DEFAULT_DELIVERY_METHODS', ['email'])
DELIVERY_METHODS = getattr(site_settings, 'NOTIFICATIONS_DELIVERY_METHODS',
	[
		('email', 'bambu.notifications.delivery.EmailDelivery')
	]
)