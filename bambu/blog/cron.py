from bambu import cron
from bambu.blog.models import Post
from datetime import datetime, timedelta
from django.utils.timezone import utc

class PostJob(cron.CronJob):
	frequency = cron.MINUTE
	
	def run(self, logger):
		date = datetime.utcnow().replace(tzinfo = utc)
		
		for post in Post.objects.filter(date__lte = date, broadcast = False):
			post.publish()
			post.save()

cron.site.register(PostJob)