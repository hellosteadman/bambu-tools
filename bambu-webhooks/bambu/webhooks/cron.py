from bambu import cron
from bambu.webhooks.models import Action

class WebHooksJob(cron.CronJob):
	frequency = cron.MINUTE
	
	def run(self, logger):
		for action in Action.objects.all():
			action.send()

cron.site.register(WebHooksJob)