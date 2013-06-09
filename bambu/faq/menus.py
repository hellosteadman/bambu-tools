from bambu import navigation

class FAQMenuBuilder(navigation.MenuBuilder):
	def register_partials(self):
		return (
			{
				'name': 'faq',
				'description': 'Adds a link to the FAQ section'
			},
		)
	
	def add_to_menu(self, name, items, **kwargs):
		items.append(
			{
				'url': ('faq_topics',),
				'title': u'FAQ',
				'selection': 'faq',
				'anon': True
			}
		)

navigation.site.register(FAQMenuBuilder)