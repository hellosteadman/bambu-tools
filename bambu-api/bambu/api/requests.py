from django.http.request import QueryDict
from django.conf import settings

class InternalRequest(object):
    def __init__(self, path, params = None):
        self.method = 'GET'
        self.path = path
        self.LANGUAGE_CODE = settings.LANGUAGE_CODE
        self.GET = params and params.copy() or QueryDict('')
