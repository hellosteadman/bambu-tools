from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from bambu.pages.models import Page
from bambu.pages.helpers import page_tree
from bambu.enqueue import enqueue_css_block

def page(request, slug):
	page = get_object_or_404(Page, slug_hierarchical = slug)
	templates = []
	parent = 'pages/'
	
	title_parts = [page.title or page.name]
	breadcrumb = [('', page.name)]
	backtick = '../'
	parent = page.parent
	styles = [enqueue_css_block(request, page.css)]
	classes = []
	
	while parent:
		templates.append('pages/%s/subpage.html' % parent.slug_hierarchical)
		templates.append(
			'pages/%ssubpage.html' % (
				'subpage/' * len(parent.slug_hierarchical.split('/'))
			)
		)
		
		title_parts.append(parent.title or parent.name)
		breadcrumb.append((backtick, parent.name))
		classes.append('subpage-%s' % parent.slug_hierarchical.replace('-', '_').replace('/', '-'))
		
		styles.append(
			enqueue_css_block(request, parent.css)
		)
		
		parent = parent.parent
		backtick += '../'
	
	breadcrumb.reverse()
	templates.insert(0, 'pages/%s.html' % page.slug_hierarchical)
	
	if page.parent:
		templates.append('pages/subpage.html')
	
	templates.append('pages/page.html')
	classes.append('page-%s' % page.slug_hierarchical.replace('-', '_').replace('/', '-'))
	
	styles.reverse()
	classes.reverse()
	
	siblings = Page.objects.filter(parent = page.parent)
	
	try:
		next = siblings.filter(order__gt = page.order)[0]
	except IndexError:
		next = None
	
	try:
		previous = siblings.filter(order__lt = page.order).order_by('-order')[0]
	except IndexError:
		previous = None
	
	return TemplateResponse(
		request,
		templates,
		{
			'page': page,
			'page_tree': page_tree(page, page.get_root_page(), show_root = True),
			'page_tree_unrooted': page_tree(page, page.get_root_page(), show_root = False),
			'title_parts': title_parts,
			'breadcrumb_trail': breadcrumb,
			'menu_selection': page.get_root_page().slug_hierarchical.replace('/', '-'),
			'enqueued_styles': styles,
			'next_page': next,
			'previous_page': previous,
			'body_classes': classes
		}
	)