from bambu import navigation

class BlogMenuBuilder(navigation.MenuBuilder):
	def register_partials(self):
		return (
			{
				'name': 'blog',
				'description': 'Adds a link to the blog'
			},
		)
	
	def add_to_menu(self, name, items, **kwargs):
		items.append(
			{
				'url': ('blog_posts',),
				'title': u'Blog',
				'selection': 'blog',
				'order': 100
			}
		)
		
navigation.site.register(BlogMenuBuilder)