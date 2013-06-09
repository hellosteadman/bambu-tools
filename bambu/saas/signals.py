from django.dispatch import Signal

newsletter_optin = Signal(providing_args = ('user',))
plan_signup = Signal(providing_args = ('plan', 'user'))
plan_subuser_added = Signal(providing_args = ('plan', 'user'))