from bambu.notifications import NotificationTemplate

comment_posted = NotificationTemplate(
	short_plain = 'A comment was submitted on "{{ comment.content_object }}"',
	short_html = 'A comment was submitted on <a href="http://{{ SITE.domain }}{{ comment.content_object.get_absolute_url }}">{{ comment.content_object }}</a>',
	short = 'A comment was submitted on "[http://{{ SITE.domain }}{{ comment.content_object.get_absolute_url }}]({{ comment.content_object }})"',
	long = 'comments/mail.txt',
	staff_only = True,
	label = u'A user submits a comment'
)