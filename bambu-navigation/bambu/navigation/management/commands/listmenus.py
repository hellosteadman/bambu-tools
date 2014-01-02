from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	help = 'List the menus registered for this site'
	
	def handle(self, *args, **options):
		from bambu.navigation import site, autodiscover
		
		autodiscover()
		print
		print 'You can use the following menu partials in your NAVIGATION_MENUS setting'
		
		for (name, description) in site._partials:
			print '- %s%s' % (name.ljust(20, ' '), description)
		
		names = ', '.join(["'%s'" % n for (n, d) in site._partials])
		
		print
		print 'For example:'
		print
		print '>>> NAVIGATION_MENUS = (\n... \t\'your-menu-key\', (' + names + ')\n... )'
		
		print
		print 'This will create a menu that contains all of the above items'
		print
		print 'To include this menu in your template, add'
		print
		print '{% load navigation %}\n{% menu \'your-menu-key\' %}...{% endmenu %}'
		print