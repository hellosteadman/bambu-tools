from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from bambu.mail.shortcuts import render_to_mail
from django.contrib.auth.models import User
import requests, logging

AKISMET_URL = 'http://%s.rest.akismet.com/1.1/comment-check'
LOGGER = logging.getLogger('bambu.comments')

class Enquiry(models.Model):
	name = models.CharField(max_length = 50)
	email = models.EmailField(max_length = 200, db_index = True)
	subject = models.CharField(max_length = 500)
	message = models.TextField()
	sent = models.DateTimeField(auto_now_add = True, db_index = True)
	
	def __unicode__(self):
		return self.subject
	
	def check_for_spam(self, request):
		akismet = getattr(settings, 'AKISMET_KEY', '')
		if not akismet:
			return False
		
		LOGGER.debug('Checking comment for spam')
		ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
		user_agent = request.META.get('USER_AGENT')
		referrer = request.META.get('HTTP_REFERER')
		
		site = Site.objects.get_current()
		response = requests.post(AKISMET_URL % akismet,
			data = {
				'blog': 'http://%s/' % (site.domain),
				'user_ip': ip,
				'user_agent': user_agent,
				'referrer': referrer,
				'permalink': 'http://%s%s' % (site.domain, request.GET.get('next', request.path)),
				'comment_type': 'enquiry',
				'comment_author': self.name,
				'comment_author_email': self.email,
				'comment_content': self.message
			}
		)
		
		if response.content == 'true':
			return True
		
		if response.content == 'false':
			return False
		
		LOGGER.warn('Unexpected response from Akismet: %s' % response.content)
	
	def save(self, *args, **kwargs):
		notify = kwargs.pop('notify', True)
		super(Enquiry, self).save(*args, **kwargs)
		
		if notify:
			site = Site.objects.get_current()
			
			render_to_mail(
				subject = u'Enquiry from %s' % site.name,
				template = 'enquiries/mail.txt',
				context = {
					'name': self.name,
					'email': self.email,
					'subject': self.subject,
					'message': self.message
				},
				recipient = [
					u for u in User.objects.filter(is_staff = True)
				]
			)
	
	class Meta:
		verbose_name_plural = 'enquiries'
		ordering = ('-sent',)
		get_latest_by = 'sent'