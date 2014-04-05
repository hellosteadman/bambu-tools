from django.db import models
from django.utils.timezone import pytz
from bambu.buffer.settings import PROFILES_URL, TIMEOUT
from bambu.buffer import log
from datetime import datetime, timedelta
import requests, json

class BufferToken(models.Model):
    user = models.ForeignKey('auth.User', related_name = 'buffer_tokens', unique = True)
    token = models.CharField(max_length = 36)

    def __unicode__(self):
        return self.token

    def save(self, *args, **kwargs):
        new = not self.pk
        super(BufferToken, self).save(*args, **kwargs)

        if new:
            self.refresh_services()

    def refresh_services(self):
        response = requests.get(
            '%s?access_token=%s' % (
                PROFILES_URL,
                self.token
            ),
            timeout = TIMEOUT
        )

        if response.status_code == 200:
            self.services.all().delete()
            services = {}
            for profile in response.json():
                remote_id = profile['formatted_service']
                if remote_id in services:
                    service = services[remote_id]
                else:
                    service = self.services.create(
                        remote_id = profile[u'service_id'],
                        name = remote_id,
                        username = profile['service_username']
                    )

                    services[service.remote_id] = service

                epoch = datetime(1970, 1, 1, 0, 0, 0,
                    tzinfo = pytz.timezone(
                        profile['timezone']
                    )
                )

                service.profiles.create(
                    avatar = profile.get('avatar_https',
                        profile.get('avatar')
                    ),
                    created_at = epoch + timedelta(
                        seconds = profile['created_at']
                    ),
                    default = profile['default'],
                    selected = profile['default'],
                    formatted_username = profile['formatted_username'],
                    remote_id = profile['id'],
                    schedules = json.dumps(
                        profile['schedules']
                    )
                )
        else:
            log.error(response.json(), request)

    class Meta:
        db_table = 'buffer_token'

class BufferService(models.Model):
    token = models.ForeignKey(BufferToken, related_name = 'services')
    name = models.CharField(max_length = 30)
    remote_id = models.CharField(max_length = 36)
    username = models.CharField(max_length = 30)

    def __unicode__(self):
        return self.name

    @property
    def icon(self):
        return self.name.lower().split(' ')[0].replace('+', '-plus')

    class Meta:
        db_table = 'buffer_service'

class BufferProfile(models.Model):
    service = models.ForeignKey(BufferService, related_name = 'profiles')
    avatar = models.URLField(max_length = 255)
    created_at = models.DateTimeField()
    default = models.BooleanField(default = True)
    formatted_username = models.CharField(max_length = 100)
    remote_id = models.CharField(max_length = 36, unique = True)
    schedules = models.TextField()
    selected = models.BooleanField()

    def __unicode__(self):
        return self.formatted_username

    @property
    def icon(self):
        return self.service.icon

    class Meta:
        db_table = 'buffer_profile'
