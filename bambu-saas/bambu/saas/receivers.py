from bambu.saas.signals import newsletter_optin, plan_signup

def payment_complete(sender, payment, **kwargs):
	payment.content_object.paid = True
	payment.content_object.save()
	
	for group in payment.content_object.plan.groups.all():
		payment.content_object.user.groups.add(group)
	
	if payment.content_object.user.pending_newsletter_optins.count() == 1:
		newsletter_optin.send(
			type(payment.content_object.user),
			user = payment.content_object.user
		)
		
		payment.content_object.user.pending_newsletter_optins.all().delete()
	
	plan_signup.send(
		type(payment.content_object.plan),
		plan = payment.content_object.plan,
		user = payment.content_object.user
	)

def payment_complete_change(sender, payment, **kwargs):
	payment.content_object.paid = True
	payment.content_object.save()

def payment_cancelled(sender, payment, **kwargs):
	payment.content_object.user.delete()

def payment_error(sender, payment, **kwargs):
	payment.content_object.user.delete()

def payment_terminated(sender, payment, **kwargs):
	payment.content_object.user.delete()