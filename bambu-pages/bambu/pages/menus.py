from bambu import navigation
from bambu.pages.models import Page

class PageMenuBuilder(navigation.MenuBuilder):
	def register_partials(self):
		yield {
			'name': 'pages',
			'description': 'Lists all the root-level pages in the site'
		}
	
	def add_to_menu(self, name, items, menu_name = None, **kwargs):
		pages = Page.objects.root()
		
		if menu_name:
			pages = pages.menu(menu_name)
		
		for page in pages:
			items.append(
				{
					'url': ('page', [page.slug_hierarchical]),
					'title': page.name,
					'selection': page.get_root_page().slug_hierarchical.replace('/', '-'),
					'order': 10 + page.order
				}
			)

navigation.site.register(PageMenuBuilder)