from django.db.models import Manager

class PostManager(Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def live(self):
		return self.get_query_set().live()
	
	def css(self, rendered = False):
		return self.get_query_set().css(rendered)