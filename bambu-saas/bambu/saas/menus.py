from bambu import navigation

class SAASMenuBuilder(navigation.MenuBuilder):
	def register_partials(self):
		return (
			{
				'name': 'profile',
				'description': 'Adds links to view a user\'s dashboard'
			},
			{
				'name': 'profile:edit',
				'description': 'Adds links to edit a user\'s profile'
			},
			{
				'name': 'saas',
				'description': 'Adds links to the Plans & Pricing page'
			}
		)
	
	def add_to_menu(self, name, items, **kwargs):
		if name in ('profile', 'profile:edit'):
			items.append(
				{
					'url': ('profile',),
					'title': u'Account',
					'title_long': u'View your dashboard',
					'selection': 'profile',
					'login': True,
					'order': 10,
					'icon': 'dashboard'
				}
			)
		
		if name == 'profile:edit':
			items.append(
				{
					'url': ('profile_edit',),
					'title': u'Edit account',
					'title_long': u'Edit your account details',
					'selection': 'profile:edit',
					'login': True,
					'order': 10,
					'icon': 'user'
				}
			)
			
			items.append(
				{
					'url': ('profile_subusers',),
					'title': u'Teammates',
					'title_long': u'Manage teammates',
					'selection': 'profile:subusers',
					'login': True,
					'order': 20,
					'icon': 'group',
					'perms': ('saas.change_subuser',)
				}
			)
		elif name != 'profile':
			items.append(
				{
					'url': ('plans',),
					'title': u'Plans and pricing',
					'selection': 'plans',
					'highlight': True,
					'anon': True
				}
			)

navigation.site.register(SAASMenuBuilder)