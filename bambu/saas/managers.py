from django.db.models import Manager, Sum, Q
from django.conf import settings
from bambu.saas import helpers

class PlanManager(Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def matrix(self, currency = None):
		return self.get_query_set().matrix(
			currency or getattr(settings, 'CURRENCY_CODE', 'GBP')
		)

class UserPlanManager(Manager):
	def get_for_user(self, user):
		try:
			return self.model.objects.distinct().get(user = user)
		except self.model.DoesNotExist, ex:
			try:
				return self.model.objects.distinct().filter(subusers = user).order_by('-plan__order')[0]
			except IndexError:
				raise ex