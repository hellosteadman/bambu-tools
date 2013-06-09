from bambu.notifications import NotificationTemplate

subuser_registered = NotificationTemplate(
	short = '{{ user.get_full_name|default:user.username }} has joined your team',
	long = 'saas/notifications/joined.txt',
	label = u'Someone joined your team'
)