from bambu import cron

cron.autodiscover()
class CronMiddleware(object):
	def process_request(self, *args, **kwargs):
		cron.site.run()