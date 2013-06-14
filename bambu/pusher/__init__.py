from django.conf import settings
from django.utils import simplejson
from django.utils.http import urlencode
from django.utils.timezone import now
import requests, time, hmac, hashlib, base64

APP_ID = getattr(settings, 'PUSHER_APP_ID', None)
KEY = getattr(settings, 'PUSHER_KEY', None)
SECRET = getattr(settings, 'PUSHER_SECRET', None)
VERSION = '1.0'
DOMAIN = 'api.pusherapp.com'
PATH = '/apps/%s/events' % APP_ID

def push(channel, event, **data):
	json = simplejson.dumps(
		{
			'name': event,
			'channel': channel,
			'data': simplejson.dumps(data)
		}
	)
	
	params = {
		'auth_key': KEY,
		'auth_timestamp': str(int(time.mktime(now().timetuple()))),
		'auth_version': VERSION,
		'body_md5': hashlib.md5(json).hexdigest()
	}
	
	hashparts = []
	for key in sorted(params.keys()):
		hashparts.append(
			'%s=%s' % (key, params[key])
		)
	
	msg = 'POST\n%s\n%s' % (
		PATH, '&'.join(hashparts)
	)
	
	params['auth_signature'] = hmac.new(SECRET,
		msg = msg,
		digestmod = hashlib.sha256
	).hexdigest()
	
	response = requests.post(
		'http://%s%s?%s' % (
			DOMAIN, PATH, urlencode(params)
		),
		json,
		headers = {
			'Content-Type': 'application/json'
		}
	)
	
	return response and response.status_code == 200