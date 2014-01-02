from bambu.notifications import NotificationTemplate

import_success = NotificationTemplate(
	short = 'Importing {{ job.name }} was successful',
	long = 'dataportability/notifications/success.txt',
	label = u'A data import was successful'
)

import_fail = NotificationTemplate(
	short = 'Importing {{ job.name }} was not successful',
	long = 'dataportability/notifications/fail.txt',
	label = u'A data import failed'
)