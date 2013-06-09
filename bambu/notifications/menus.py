from bambu import navigation

class HotificationsMenuBuilder(navigation.MenuBuilder):
	def register_partials(self):
		return (
			{
				'name': 'profile:edit',
				'description': 'Adds links to edit a user\'s notification settings'
			},
		)
	
	def add_to_menu(self, name, items, **kwargs):
		items.append(
			{
				'url': ('notifications_manage',),
				'title': u'Notifications',
				'title_long': u'Notification settings',
				'selection': 'profile:notifications',
				'login': True,
				'order': 20,
				'icon': 'bell-alt'
			}
		)

navigation.site.register(HotificationsMenuBuilder)