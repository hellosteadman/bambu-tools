from copy import deepcopy

class NotificationTemplate(object):
	def __init__(self, **kwargs):
		self.label = kwargs.pop('label', None)
		self.staff_only = kwargs.pop('staff_only', False)
		self.templates = deepcopy(kwargs)
		self.perms = kwargs.pop('perms', ())