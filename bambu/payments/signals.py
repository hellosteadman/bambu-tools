from django.dispatch import Signal

payment_complete = Signal(providing_args = ('payment',))
payment_cancelled = Signal(providing_args = ('payment',))
payment_error = Signal(providing_args = ('payment',))
payment_terminated = Signal(providing_args = ('payment',))