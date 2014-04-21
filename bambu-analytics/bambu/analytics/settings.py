from django.conf import settings as s

PROVIDER = getattr(s, 'ANALYTICS_PROVIDER',
    'bambu.analytics.providers.google.UniversalAnalyticsProvider'
)

def get(klass):
    return getattr(s,
        'ANALYTICS_SETTINGS', {
            klass: {}
        }
    ).get(klass)
