from django.db.models import Manager

class PageManager(Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def root(self):
		return self.get_query_set().root()
	
	def menu(self, name):
		return self.get_query_set().menu(name)