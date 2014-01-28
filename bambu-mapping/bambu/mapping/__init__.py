from django.conf import settings

__version__ = '0.1'
PROVIDER = getattr(settings, 'MAPPING_PROVIDER',
	'bambu.mapping.providers.OpenStreetMapProvider'
)