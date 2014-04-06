from django.conf import settings as s
from django.utils.timezone import now

CLIENT_ID = s.BUFFER_CLIENT_ID
CLIENT_SECRET = s.BUFFER_CLIENT_SECRET
AUTH_REDIRECT = getattr(s, 'BUFFER_AUTH_REDIRECT', '/')
SUCCESS_MESSAGE = getattr(s, 'BUFFER_SUCCESS_MESSAGE',
    u'Your Buffer account is now conntected.'
)

ERROR_MESSAGE = getattr(s, 'BUFFER_ERROR_MESSAGE',
    u'Sorry, your account could not be connected to Buffer: %s.'
)

UPDATED_MESSAGE = getattr(s, 'BUFFER_UPDATED_MESSAGE',
    u'Your Buffer settings have been updated.'
)

REFRESHED_MESSAGES = getattr(s, 'BUFFER_REFRESHED_MESSAGES',
    u'Your Buffer profiles have been refreshed.'
)

AUTOPOST_MODELS = getattr(s, 'BUFFER_AUTOPOST_MODELS',
    (
        (
            'blog.Post',
            'author', {
                'published': True,
                'date__lte': now
            },
            {
                'top': True
            }
        ),
    )
)

TIMEOUT = getattr(s, 'BUFFER_TIMEOUT', 5)
AUTHORISE_URL = 'https://bufferapp.com/oauth2/authorize'
TOKEN_URL = 'https://api.bufferapp.com/1/oauth2/token.json'
PROFILES_URL = 'https://api.bufferapp.com/1/profiles.json'
POST_URL = 'https://api.bufferapp.com/1/updates/create.json'
RESPONSE_TYPE = 'code'
AUTHORISATION_CODE = 'authorization_code'
