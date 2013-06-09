from bambu.pages.models import Page

def page_or_parent_selected(page, selected):
	if page.pk == selected.pk:
		return True
	
	while True:
		selected = selected.parent
		if selected:
			if page.pk == selected.pk:
				return True
		else:
			break
	
	return False

def page_tree(selected = None, parent = None, show_root = False):
	items = []
	
	if parent and show_root and parent.children.exists():
		if selected and parent.pk == selected.pk:
			is_selected = ' class="active"'
		else:
			is_selected = ''
		
		items.append(
			'<li%s><a href="%s">%s</a>%s</li>' % (
				is_selected,
				parent.get_absolute_url(),
				parent.name,
				page_tree(selected, parent)
			)
		)
	else:
		for page in Page.objects.select_related().filter(parent = parent):
			if selected and page_or_parent_selected(page, selected):
				is_selected = ' class="active"'
			else:
				is_selected = ''
			
			items.append(
				'<li%s><a href="%s">%s</a>%s</li>' % (
					is_selected,
					page.get_absolute_url(),
					page.name,
					page_tree(selected, page)
				)
			)
	
	if len(items) > 0:
		return '<ol class="page-navigation">%s</ol>' % ''.join(items)
	else:
		return ''