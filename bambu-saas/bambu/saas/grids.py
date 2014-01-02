from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.http import urlencode
from django.conf import settings
from django.core.urlresolvers import reverse
from hashlib import md5
from bambu import grids
from bambu.saas.models import Invitation

class SubuserGrid(grids.ModelGrid):
	model = User
	columns = ('avatar', 'username', 'first_name', 'last_name', 'email_link')
	column_attrs = (
		{
			'width': '50'
		},
		{
			'width': '10%',
			'style': 'white-space: nowrap'
		},
		{},
		{},
		{
			'width': '20%',
			'style': 'white-space: nowrap'
		},
		{
			'width': '5%',
			'style': 'white-space: nowrap'
		}
	)
	
	def __init__(self, *args, **kwargs):
		super(SubuserGrid, self).__init__(*args, **kwargs)
		self._site = Site.objects.get_current()
		
		static_url = getattr(settings, 'STATIC_URL')
		if static_url:
			if static_url.startswith('//'):
				self._static = 'http:%s' % static_url
			elif not (static_url.startswith('http://') or static_url.startswith('https://')):
				self._static = 'http://%s%s' % (self._site.domain, static_url)
			else:
				self._static = static_url
		else:
			self._static = 'http://%s/static/' % self._site.domain
	
	actions = ('remove',)
	
	def avatar(self, obj):
		if not obj.email:
			return u''
		
		return u'<img src="//www.gravatar.com/avatar/%s.jpg?%s" width="50" height="50">' % (
			md5(obj.email).hexdigest(),
			urlencode(
				{
					'd': '%ssaas/img/avatar.png' % self._static,
					's': 100
				}
			)
		)
	avatar.safe = True
	
	def email_link(self, obj):
		if obj.email:
			return '<a href="mailto:%(email)s">%(email)s' % {
				'email': obj.email
			}
		else:
			return u''
	email_link.link = False
	email_link.safe = True
	email_link.friendly_name = 'E-mail address'
	
	def remove(self, obj):
		return reverse('profile_delete_subuser', args = [obj.username])
	remove.classes = ('btn', 'btn-danger')
	remove.icon = 'remove'
	remove.icon_colour = 'white'

class InvitationGrid(grids.ModelGrid):
	model = Invitation
	columns = ('avatar', 'email_link')
	column_attrs = (
		{
			'width': '50'
		},
		{
			'width': '5%',
			'style': 'white-space: nowrap'
		}
	)
	
	actions = ('resend', 'remove',)
	visible_actions = 2
	
	def __init__(self, *args, **kwargs):
		super(InvitationGrid, self).__init__(*args, **kwargs)
		self._site = Site.objects.get_current()
		
		static_url = getattr(settings, 'STATIC_URL')
		if static_url:
			if static_url.startswith('//'):
				self._static = 'http:%s' % static_url
			elif not (static_url.startswith('http://') or static_url.startswith('https://')):
				self._static = 'http://%s%s' % (self._site.domain, static_url)
			else:
				self._static = static_url
		else:
			self._static = 'http://%s/static/' % self._site.domain
	
	def avatar(self, obj):
		if not obj.email:
			return u''
		
		return u'<img src="//www.gravatar.com/avatar/%s.jpg?%s" width="50" height="50">' % (
			md5(obj.email).hexdigest(),
			urlencode(
				{
					'd': '%ssaas/img/avatar.png' % self._static,
					's': 100
				}
			)
		)
	avatar.safe = True
	
	def email_link(self, obj):
		if obj.email:
			return '<a href="mailto:%(email)s">%(email)s' % {
				'email': obj.email
			}
		else:
			return u''
	email_link.link = False
	email_link.safe = True
	email_link.friendly_name = 'E-mail address'
	
	def resend(self, obj):
		return reverse('profile_resend_invitation', args = [obj.guid])
	resend.classes = ('btn',)
	resend.icon = 'envelope'
	resend.icon_colour = 'white'
	
	def remove(self, obj):
		return reverse('profile_delete_invitation', args = [obj.guid])
	remove.classes = ('btn', 'btn-danger')
	remove.icon = 'remove'
	remove.icon_colour = 'white'