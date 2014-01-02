from bambu import navigation

class HomeMenuBuilder(navigation.MenuBuilder):
	def register_partials(self):
		return (
			{
				'name': 'home',
				'description': 'Links to the home page'
			},
		)
	
	def add_to_menu(self, name, items, **kwargs):
		items.append(
			{
				'url': ('home',),
				'title': u'Home',
				'selection': u'home',
				'order': -1
			}
		)
		
navigation.site.register(HomeMenuBuilder)