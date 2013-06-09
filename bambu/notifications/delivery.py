from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.template.defaultfilters import linebreaks, striptags
from django.utils.safestring import mark_safe
from markdown import markdown

class DeliveryBase(object):
	longform = False
	verbose_name = ''
	
	def deliver(self, user, versions, actions):
		pass

class EmailDelivery(object):
	longform = True
	verbose_name = 'Send an email'
	
	def deliver(self, user, versions, actions):
		if not user.email:
			return
		
		from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
		site = Site.objects.get_current()
		
		if 'long' in versions:
			body = versions['long']
		elif 'long_plain' in versions:
			body = versions['long_plain']
		elif 'long_html' in versions:
			body = striptags(markdown(versions['long_html']))
		elif 'short' in versions:
			body = versions['short']
		elif 'short_plain' in versions:
			body = versions['short_plain']
		elif 'short_html' in versions:
			body = striptags(markdown(versions['short_html']))
		
		media_url = settings.MEDIA_URL
		static_url = getattr(settings, 'STATIC_URL', '/static')

		if media_url.startswith('//'):
			media_url = 'http:%s' % media_url
		elif not (media_url.startswith('http://') or media_url.startswith('https://')):
			media_url = 'http://%s%s' % (site.domain, media_url)

		if static_url.startswith('//'):
			static_url = 'http:%s' % static_url
		elif not (static_url.startswith('http://') or static_url.startswith('https://')):
			static_url = 'http://%s%s' % (site.domain, static_url)
		
		ctx = {
			'MEDIA_URL': media_url,
			'STATIC_URL': static_url,
			'SITE': site,
			'body': body,
			'actions': actions
		}
		
		if ctx['MEDIA_URL'].startswith('/'):
			ctx['MEDIA_URL'] = 'http://%s%s' % (ctx['SITE'].domain, ctx['MEDIA_URL'])
		
		email = EmailMultiAlternatives(
			versions.get('short_plain') or striptags(markdown(versions.get('short'))) or striptags(versions.get('short_html')),
			render_to_string('notifications/mail/base.txt', ctx),
			from_email,
			[
				'%s <%s>' % (
					user.get_full_name() or user.username,
					user.email
				)
			]
		)
		
		if 'long_html' in versions:
			ctx['body'] = mark_safe(versions['long_html'])
		elif 'long' in versions:
			ctx['body'] = markdown(versions['long'])
		elif 'long_plain' in versions:
			ctx['body'] = linebreaks(versions['long_plain'])
		elif 'short_html' in versions:
			ctx['body'] = mark_safe(versions['short_html'])
		elif 'short' in versions:
			ctx['body'] = markdown(versions['short'])
		elif 'short_plain' in versions:
			ctx['body'] = linebreaks(versions['short_plain'])
		
		email.attach_alternative(
			render_to_string('notifications/mail/base.html', ctx),
			"text/html"
		)
		
		try:
			email.send()
		except:
			pass