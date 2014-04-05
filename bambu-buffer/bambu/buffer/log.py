from django.contrib import messages
from django.utils.translation import ugettext as _
from bambu.buffer.settings import SUCCESS_MESSAGE, ERROR_MESSAGE
from bambu.buffer.exceptions import BufferException
import logging

logger = logging.getLogger('bambu.buffer')
def error(data, request = None, raise_error = False):
    error = data.get('error_description',
        data.get('message',
            'error' in data and data.get('error').capitalize().replace('_', ' ') or ''
        )
    ) or u'Unknown error'

    if 'message' in data:
        data['error_message'] = data.pop('message')
    
    logger.error(error, extra = data)

    if request and ERROR_MESSAGE:
        messages.error(request,
            _(ERROR_MESSAGE) % error
        )

    if raise_error:
        raise BufferException(error)

def success(data, request = None):
    message = None
    if 'access_token' in data:
        message = u'Buffer access token created'

    if message:
        logger.info(message)

        if request and SUCCESS_MESSAGE:
            messages.success(request,
                _(SUCCESS_MESSAGE)
            )
