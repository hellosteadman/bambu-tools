from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from os import sys

class Command(BaseCommand):
    help = 'Fake Buffer records for items in settings.BUFFER_AUTOPOST_MODELS'

    @transaction.commit_on_success
    def handle(self, *args, **options):
        from django.contrib.contenttypes.models import ContentType
        from bambu.buffer import site
        from bambu.buffer.models import BufferedItem

        for model, info in site._registry.items():
            query = dict(
                [
                    (key, callable(value) and value() or value)
                    for (key, value) in info['conditions'].items()
                ]
            )

            count = 0
            for pk in model.objects.filter(**query).values_list('pk', flat = True):
                item, created = BufferedItem.objects.get_or_create(
                    content_type = ContentType.objects.get_for_model(model),
                    object_id = pk
                )

                if not created:
                    count += 1

            sys.stdout.write(
                'Added fake Buffer item for %d %s\n' % (
                    count,
                    unicode(
                        count == 1 and model._meta.verbose_name or model._meta.verbose_name_plural
                    )
                )
            )
