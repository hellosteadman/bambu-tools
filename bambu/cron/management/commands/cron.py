from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

class Command(BaseCommand):
	help = 'Run tasks at scheduled intervals'
	option_list = BaseCommand.option_list + (
		make_option('--setup',
			action = 'store_true',
			dest = 'setup',
			default = False,
			help = 'Setup cron jobs and run only those that are due'
		),
		make_option('--force',
			action = 'store_true',
			dest = 'force',
			default = False,
			help = 'Run all cron jobs, including ones that aren\'t scheduled yet'
		),
		make_option('--debug',
			action = 'store_true',
			dest = 'debug',
			default = False,
			help = 'Raise errors when they occur, rather than log them'
		)
	)
	
	def handle(self, *args, **options):
		from django.conf import settings
		from bambu import cron
		from os import path, remove
		import logging, time
		
		flag = getattr(settings, 'CRON_FLAG_FILE', None)
		logger = logging.getLogger('bambu.cron')
		
		if flag and path.exists(flag):
			logger.debug('Cron flag file "%s" already set; abandoning' % flag)
			return
		
		cron.autodiscover()
		if options['setup']:
			cron.site.setup()
		
		if flag:
			logger.debug('Setting flag file "%s"' % flag)
			open(flag, 'w').write(
				str(time.time())
			)
		
		try:
			cron.site.run(options['force'], options['debug'])
		finally:
			if flag and path.exists(flag):
				logger.debug('Removing flag file "%s"' % flag)
				remove(flag)