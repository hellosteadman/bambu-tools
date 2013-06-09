from django.db.models import Manager

class ContextVariableManager(Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def as_dict(self):
		return self.get_query_set().as_dict()

class NotificationManager(Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)