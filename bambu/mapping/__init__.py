from django.conf import settings

PROVIDER = getattr(settings, 'MAPPING_PROVIDER',
	'bambu.mapping.providers.OpenStreetMapProvider'
)