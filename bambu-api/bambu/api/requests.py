"""
When developing `Nymbol <https://nymbol.co.uk/>`_, I wanted to bind user-defined HTML templates
to API calls. This meant that the API functions needed to be called internally to be passed to a
system that would render the returned data as HTML. In order to reduce the amount of processing time
and power wasted in converting to and from JSON or XML, I updated Bambu API to handle 'internal'
requests by returning the data as a dict (or list of dicts), rather than an HTTP response.
"""

from django.http.request import QueryDict
from django.conf import settings

class InternalRequest(object):
    """
    Defines an internal request, by mimicking the standard Django ``HttpRequest`` class (or
    providing only the properties expected by Bambu API's various functions)
    """
    def __init__(self, path, params = None):
        self.method = 'GET'
        self.path = path
        self.LANGUAGE_CODE = settings.LANGUAGE_CODE
        self.GET = params and params.copy() or QueryDict('')
