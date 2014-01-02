from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model
from django.db import transaction
from django.contrib.auth.models import User
from django.core.files import File
from django.conf import settings
from optparse import make_option
from bambu.dataportability.models import ImportJob
from bambu.dataportability import helpers
from os import sys, path

class Command(BaseCommand):
	args = '<model object_id handler filename>'
	requires_model_validation = True
	
	option_list = BaseCommand.option_list + (
		make_option(
			'--username',
			help = 'Username of user to import data as. If not supplied, the first superuser is selected'
		),
	)
	
	help = 'Import data'
	
	def handle(self, *args, **options):
		handlers = getattr(settings, 'DATAPORTABILITY_HANDLERS', {})
		
		try:
			model, obj_id, handler, filename = args
		except ValueError:
			raise CommandError('Specify the model, object ID, import handler and filename to base the import on')
		
		if options['username']:
			try:
				user = User.objects.get(username = options['username'])
			except User.DoesNotExist:
				raise CommandError('User %s not found' % options['username'])
		else:
			try:
				user = User.objects.filter(is_superuser = True)[0]
			except IndexError:
				raise CommandError('No root user found')
		
		try:
			model = get_model(*model.split('.'))
		except:
			raise CommandError('Model %s not found' % model)
		
		try:
			obj_id = int(obj_id)
		except (TypeError, ValueError):
			raise CommandError('Object ID must be an integer')
		
		try:
			obj = model.objects.get(pk = obj_id)
		except model.DoesNotExist:
			raise CommandError(
				'%s with ID %d not found' % (
					model._meta.verbose_name.capitalize(), obj_id
				)
			)
		
		if not handler in handlers:
			raise CommandError('Import handler %s not found' % handler)
		
		with transaction.commit_on_success():
			job = ImportJob.objects.create(
				handler = handlers[handler],
				user = user,
				data = File(open(filename, 'r')),
				parser = helpers.get_parser_for_file(
					path.split(filename)[-1]
				),
				content_object = obj
			)
			
			job.start()