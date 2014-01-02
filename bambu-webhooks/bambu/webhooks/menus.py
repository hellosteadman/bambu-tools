from bambu import navigation

class WebHooksMenuBuilder(navigation.MenuBuilder):
	def register_partials(self):
		return (
			{
				'name': 'profile:edit',
				'description': 'Adds links to edit a user\'s webhooks'
			},
		)
	
	def add_to_menu(self, name, items, **kwargs):
		items.append(
			{
				'url': ('webhooks_manage',),
				'title': u'Webhooks',
				'title_long': u'Manage webhooks',
				'selection': 'profile:webhooks',
				'login': True,
				'order': 30,
				'icon': 'cogs',
				'perms': ('webhooks.change_webhook',)
			}
		)

navigation.site.register(WebHooksMenuBuilder)