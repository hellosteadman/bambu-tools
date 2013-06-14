from bambu import cron
from bambu.blog.models import Post
from django.utils.timezone import now

class PostJob(cron.CronJob):
	frequency = cron.MINUTE
	
	def run(self, logger):
		date = now()
		
		for post in Post.objects.filter(date__lte = date, broadcast = False):
			post.publish()
			post.save()

cron.site.register(PostJob)