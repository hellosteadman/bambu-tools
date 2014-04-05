from django.contrib.sites.models import Site
from django.db.models import Model
from bambu.buffer.exceptions import *
from bambu.buffer.models import BufferToken, BufferProfile
from bambu.buffer.settings import POST_URL, TIMEOUT
from bambu.buffer import log
from datetime import datetime, date
from threading import Thread
import requests

class BufferThread(Thread):
    def __init__(self, token, data, *args, **kwargs):
        self.data = data
        self.token = token
        super(BufferThread, self).__init__(*args, **kwargs)

    def run(self):
        response = requests.post(
            '%s?access_token=%s' % (POST_URL, self.token),
            self.data,
            timeout = TIMEOUT
        )

        if response.status_code != 200:
            log.error(response.json())

def post(item, author, **kwargs):
    try:
        token = author.buffer_tokens.get()
    except BufferToken.DoesNotExist:
        return

    if 'url' in kwargs:
        url = kwargs.get('url')
    elif isinstance(item, Model):
        url = u'http://%s%s' % (
            site.domain, item.get_absolute_url()
        )
    else:
        url = None

    site = Site.objects.get_current()
    data = {
        'text': kwargs.get('text') or unicode(item),
        'profile_ids[]': kwargs.get('profile_ids') or BufferProfile.objects.filter(
            service__token = token,
            selected = True
        ).values_list('remote_id', flat = True),
        'media[description]': kwargs.get('description')
    }

    if url:
        data['media[link]'] = url

    if 'picture' in kwargs:
        data['media[picture]'] = kwargs['picture']
        if not 'thumbnail' in kwargs:
            raise TypeError(
                'For image-based updates, the thumbnail parameter is required.'
            )

    if 'thumbnail' in kwargs:
        data['media[thumbnail]'] = kwargs['thumbnail']

    if 'shorten' in kwargs:
        data['shorten'] = kwargs['shorten'] and 'true' or 'false'

    if 'now' in kwargs:
        data['now'] = kwargs['now'] and 'true' or 'false'

    if 'top' in kwargs:
        data['top'] = kwargs['top'] and 'true' or 'false'

    if 'scheduled_at' in kwargs:
        if isinstance(kwargs['scheduled_at'], (datetime, date)):
            data['scheduled_at'] = kwargs['scheduled_at'].isoformat()
        else:
            try:
                data['scheduled_at'] = int(kwargs['scheduled_at'])
            except:
                raise TypeError(
                    'scheduled_at must be an integer or DateTime'
                )

    BufferThread(token.token, data).start()
