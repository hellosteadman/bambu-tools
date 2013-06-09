from bambu.mail.shortcuts import subscribe

def newsletter_optin(sender, user, **kwargs):
	subscribe(
		user.email,
		list_id = 'signup',
		double_optin = False,
		send_welcome = False
	)