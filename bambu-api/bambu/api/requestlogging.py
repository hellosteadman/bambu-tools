"""
It's possible to throttle the number of requests sent to Bambu API by using or defining a
request logger. These loggers take note of the numbers of requests within a given timeframe by
a specific app, and validate incoming requests against that value.
"""

from django.utils.timezone import get_current_timezone, now
from django.db.models import F
from django.db import transaction
from django.conf import settings
from datetime import datetime
from logging import getLogger
import pickle

THROTTLE_REQUESTS = getattr(settings, 'API_THROTTLE_REQUESTS', 60)
THROTTLE_MINUTES = getattr(settings, 'API_THROTTLE_MINUTES', 1)
EPOCH = datetime(1970, 1, 1).replace(tzinfo = get_current_timezone())

class RequestLoggerBase(object):
    """The base request logger"""
    def log_request(self, app):
        raise NotImplementedError('Method not implemented.')

    def get_timestamp(self):
        """
        Gets a timestamp for the current timeframe. For example, if the API allows 1,000 requests per
        minute, the timestamp would be the standard UNIX timestamp (number of seconds from the Epoch),
        divided by 60, rounded up and multiplied by 60.
        """

        def total_seconds(td):
            if hasattr(td, 'total_seconds'):
                return td.total_seconds()
            else:
                return td.days * 24 * 60 * 60 + getattr(td, 'seconds', 0)

        seconds = max(1.0, float(THROTTLE_MINUTES * 60))
        return int(total_seconds(now() - EPOCH) / seconds) * 60

    def validate_request(self, app):
        """
        Returns ``True`` when the request is allowed, or ``False`` if there have been too many
        requests by the specified app within the specified timeframe (as determined by
        ``get_request_count()``)
        """
        if THROTTLE_MINUTES > 0:
            count = self.get_request_count(
                app, self.get_timestamp()
            )

            try:
                if count > THROTTLE_REQUESTS:
                    return False
            except IndexError:
                pass

        return True

    def get_request_count(self, app, timestamp):
        raise NotImplementedError('Method not implemented.')

class DatabaseRequestLogger(RequestLoggerBase):
    """The default request logger"""
    def log_request(self, app):
        """Saves the number of requests within the given timeframe to the database"""
        timestamp = self.get_timestamp()

        with transaction.commit_on_success():
            app.requests.get_or_create(timestamp = timestamp)
            app.requests.update(count = F('count') + 1)
            app.requests.filter(timestamp__lt = timestamp).delete()

    def get_request_count(self, app, timestamp):
        """Returns the number of requests by the specified app, within the specified timeframe"""
        try:
            return app.requests.filter(timestamp = timestamp).values_list('count', flat = True)[0]
        except IndexError:
            return 0

class RedisRequestLogger(RequestLoggerBase):
    """A faster alternative to the default logger, but requiring more configuration"""

    def __init__(self):
        from redis import StrictRedis

        super(RedisRequestLogger, self).__init__()
        self.db = StrictRedis(
            host = getattr(settings, 'API_REDIS_HOST', 'localhost'),
            port = getattr(settings, 'API_REDIS_PORT', 6379),
            db = getattr(settings, 'API_REDIS_DB', 0),
            password = getattr(settings, 'API_REDIS_PASSWORD', '')
        )

    def get_key(self, app):
        return 'bambu-api-requests-%s' % app.key

    def log_request(self, app):
        """Saves the number of requests within the given timeframe to the Redis database"""

        timestamp = self.get_timestamp()
        key = self.get_key(app)
        values = self.db.get(key)

        if values:
            try:
                values = pickle.loads(values)
            except:
                values = {}
        else:
            values = {}

        if values.has_key(timestamp):
            values = {
                timestamp: values[timestamp] + 1
            }
        else:
            values = {
                timestamp: 1
            }

        self.db.set(key, pickle.dumps(values))

    def get_request_count(self, app, timestamp):
        """Returns the number of requests by the specified app, within the specified timeframe"""

        values = self.db.get(
            self.get_key(app)
        )

        if values:
            try:
                values = pickle.loads(values)
            except:
                values = {}
        else:
            values = {}

        return values.get(timestamp) or 0
