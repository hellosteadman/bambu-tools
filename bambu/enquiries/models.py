from django.db import models

class Enquiry(models.Model):
	name = models.CharField(max_length = 50)
	email = models.EmailField(max_length = 200, db_index = True)
	subject = models.CharField(max_length = 500)
	message = models.TextField()
	sent = models.DateTimeField(auto_now_add = True, db_index = True)
	
	def __unicode__(self):
		return self.subject
	
	def save(self, *args, **kwargs):
		from bambu.mail.shortcuts import render_to_mail
		from django.contrib.auth.models import User
		from django.contrib.sites.models import Site
		
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
			recipient = User.objects.filter(is_staff = True)
		)
	
	class Meta:
		verbose_name_plural = 'enquiries'
		ordering = ('-sent',)
		get_latest_by = 'sent'