from django.utils import simplejson
from bambu.webhooks.sites import WebHookSite, NotRegistered

site = WebHookSite()

def send(hook, user, data = {}, hash = None):
	if not hook in site._registry:
		raise NotRegistered('Hook %s not registered' % hook)
	
	json = simplejson.dumps(data, default = str)
	for receiver in user.webhooks.filter(hook = hook):
		receiver.cue(json, hash)