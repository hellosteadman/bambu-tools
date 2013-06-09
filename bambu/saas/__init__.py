def subusers(user):
	from bambu.saas.models import UserPlan
	
	plan = UserPlan.objects.get_for_user(user)
	return plan.subusers.count() + plan.invitations.count() + 1