from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.conf import settings
from bambu.comments.managers import *
from bambu.mail.shortcuts import render_to_mail
import requests, logging

AKISMET_URL = 'http://%s.rest.akismet.com/1.1/comment-check'
LOGGER = logging.getLogger('bambu.comments')

if 'bambu.notifications' in settings.INSTALLED_APPS:
	from bambu import notifications

class Comment(models.Model):
	name = models.CharField(max_length = 50)
	website = models.URLField(max_length = 255, null = True, blank = True)
	email = models.EmailField(max_length = 255, db_index = True)
	sent = models.DateTimeField(auto_now_add = True, db_index = True)
	approved = models.BooleanField(default = False, db_index = True)
	spam = models.BooleanField(default = False, db_index = True)
	body = models.TextField()
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField(db_index = True)
	content_object = generic.GenericForeignKey()
	objects = CommentManager()
	
	def __unicode__(self):
		return u'Re: %s' % unicode(self.content_object)
	
	def get_absolute_url(self):
		return self.content_object.get_absolute_url() + '#comment-%d' % self.pk
	
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
				'permalink': 'http://%s%s' % (site.domain, self.content_object.get_absolute_url()),
				'comment_type': 'comment',
				'comment_author': self.name,
				'comment_author_email': self.email,
				'comment_author_url': self.website,
				'comment_content': self.body
			}
		)
		
		if response.content == 'true':
			return True
		
		if response.content == 'false':
			return False
		
		LOGGER.warn('Unexpected response from Akismet: %s' % response.content)
	
	def save(self, *args, **kwargs):
		notify = kwargs.pop('notify', True)
		
		if self.spam:
			self.approved = False
		
		new = not self.pk and not self.spam
		if new and not self.approved and not self.spam:
			self.approved = Comment.objects.filter(
				email__iexact = self.email,
				approved = True,
				spam = False
			).exists()
		
		super(Comment, self).save(*args, **kwargs)
		
		if new and notify:
			if not 'bambu.notifications' in settings.INSTALLED_APPS:
				render_to_mail(
					u'New comment submitted',
					'comments/mail.txt',
					{
						'comment': self,
						'author': self.content_object.author
					},
					self.content_object.author
				)
			else:
				notifications.notify('bambu.comments.comment_posted',
					self.content_object.author,
					comment = self,
					actions = [
						{
							'urlname': 'admin:comments_comment_change',
							'args': [self.pk],
							'title': 'View the comment'
						}
					]
				)
	
	class Meta:
		ordering = ('-sent',)
		get_latest_by = 'sent'
	
	class QuerySet(models.query.QuerySet):
		def live(self):
			return self.filter(
				approved = True,
				spam = False
			)