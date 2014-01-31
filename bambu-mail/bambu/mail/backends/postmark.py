from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ImproperlyConfigured
from django.core import serializers
from django.conf import settings
import httplib2

# Original code from https://github.com/dstufft/django-postmark

try:
    import json                     
except ImportError:
    import simplejson as json

API_KEY = getattr(settings, "POSTMARK_API_KEY", None)
SSL = getattr(settings, "POSTMARK_SSL", False)
TEST_MODE = getattr(settings, "POSTMARK_TEST_MODE", False)
API_URL = ("https" if SSL else "http") + "://api.postmarkapp.com/email"

class PostmarkMailSendException(Exception):
    def __init__(self, value, inner_exception = None):
        self.parameter = value
        self.inner_exception = inner_exception

    def __str__(self):
        return repr(self.parameter)

class PostmarkMailUnauthorizedException(PostmarkMailSendException):
    pass

class PostmarkMailUnprocessableEntityException(PostmarkMailSendException):
    pass
    
class PostmarkMailServerErrorException(PostmarkMailSendException):
    pass

class PostmarkMessage(dict):
    def __init__(self, message, fail_silently = False):
        try:
            message_dict = {
                'From': message.from_email,
                'Subject': unicode(message.subject),
                'TextBody': unicode(message.body),
                'To': ','.join(message.to)
            }
            
            if len(message.cc):
                message_dict['Cc'] = ','.join(message.cc)

            if len(message.bcc):
                message_dict['Bcc'] = ','.join(message.bcc)
            
            if isinstance(message, EmailMultiAlternatives):
                for alt in message.alternatives:
                    if alt[1] == 'text/html':
                        message_dict['HtmlBody'] = unicode(alt[0])
            
            if message.extra_headers and isinstance(message.extra_headers, dict):
                if message.extra_headers.has_key('Reply-To'):
                    message_dict['ReplyTo'] = message.extra_headers.pop('Reply-To')
                    
                if message.extra_headers.has_key('X-Postmark-Tag'):
                    message_dict['Tag'] = message.extra_headers.pop('X-Postmark-Tag')
                    
                if len(message.extra_headers):
                    message_dict['Headers'] = [
                        {
                            'Name': x[0],
                            'Value': x[1]
                        } for x in message.extra_headers.items()
                    ]
            
            if message.attachments and isinstance(message.attachments, list):
                if len(message.attachments):
                    message_dict['Attachments'] = message.attachments
        
        except:
            if fail_silently:
                message_dict = {}
            else:
                raise
        
        super(PostmarkMessage, self).__init__(message_dict)

class PostmarkBackend(BaseEmailBackend):
    BATCH_SIZE = 500
    
    def __init__(self, api_key = None, api_url = None, api_batch_url = None, **kwargs):
        super(PostmarkBackend, self).__init__(**kwargs)
        
        self.api_key = api_key or API_KEY
        self.api_url = api_url or API_URL
        
        if self.api_key is None:
            raise ImproperlyConfigured(
                'POSTMARK_API_KEY must be set in Django settings file or passed to backend constructor.'
            )
    
    def send_messages(self, email_messages):
        if not email_messages:
            return
        
        num_sent = 0
        for message in email_messages:
            sent = self._send(PostmarkMessage(message, self.fail_silently))
            if sent:
                num_sent += 1
        
        return num_sent
    
    def _send(self, message):
        http = httplib2.Http()
        
        if TEST_MODE:
            print 'JSON message is:\n%s' % json.dumps(message)
            return
        
        try:
            resp, content = http.request(
                self.api_url,
                    body = json.dumps(message),
                    method = 'POST',
                    headers = {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-Postmark-Server-Token': self.api_key,
                    }
                )
        except httplib2.HttpLib2Error:
            if not self.fail_silently:
                return False
            
            raise
        
        if resp['status'] == '200':
            return True
        
        if resp['status'] == '401':
            if not self.fail_silently:
                raise PostmarkMailUnauthorizedException('Your Postmark API Key is Invalid.')
        elif resp['status'] == '422':
            if not self.fail_silently:
                content_dict = json.loads(content)
                raise PostmarkMailUnprocessableEntityException(
                    content_dict['Message']
                )
        elif resp['status'] == '500':
            if not self.fail_silently:
                PostmarkMailServerErrorException()
        
        return False