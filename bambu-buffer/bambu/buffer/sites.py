from logging import getLogger
from django.db.models.loading import get_model
from django.db.models.signals import post_save

def post_save_receiver(sender, instance, **kwargs):
    from bambu.buffer import post, site

    model = site.get_info(type(instance))
    if not model or not any(model):
        print '%s not registered' % (
            unicode(instance._meta.verbose_name).capitalize()
        )

        return

    if any(model['conditions']):
        query = dict(
            [
                (key, callable(value) and value() or value)
                for (key, value) in model['conditions'].items()
            ]
        )

        if not type(instance).objects.filter(
            pk = instance.pk,
            **query
        ).exists():
            print '%s does not match Buffer criteria' % unicode(
                unicode(instance._meta.verbose_name).capitalize()
            )

            return

    post(
        instance,
        getattr(instance,
            model['author_field']
        ),
        **dict(
            [
                (key, callable(value) and value() or value)
                for (key, value) in model['post_kwargs'].items()
            ]
        )
    )

class BufferSite(object):
    def __init__(self, *args, **kwargs):
        self._registry = {}

    def register(self, model, author_field, conditions = {}, post_kwargs = {}):
        self._registry[model] = {
            'author_field': author_field,
            'conditions': conditions,
            'post_kwargs': post_kwargs
        }

    def get_info(self, model):
        return self._registry.get(model)

    def hookup_signals(self, models):
        logger = getLogger('bambu.buffer')
        for m in [list(m) for m in models]:
            if not any(m):
                continue

            name = m.pop(0)
            if any(m):
                author_field = m.pop(0)
            else:
                author_field = 'author'

            if any(m):
                conditions = m.pop(0)
            else:
                conditions = {}

            if any(m):
                post_kwargs = m.pop(0)
            else:
                post_kwargs = {}

            try:
                model = get_model(*name.split('.'))
            except:
                logger.warn('Model %s not found' % name)
                continue

            field = model._meta.get_field_by_name(author_field)
            if not any(field) or field[0] is None:
                raise Exception(
                    'Field %s not found in model %s' % (author_field, name)
                )

            self.register(model,
                author_field = author_field,
                conditions = conditions,
                post_kwargs = post_kwargs
            )

            post_save.connect(post_save_receiver, sender = model)
