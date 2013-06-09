from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from bambu.faq.models import Category, Topic

def topics(request, category = None):
	if category:
		category = get_object_or_404(Category, slug = category)
		topics = Topic.objects.filter(category = category)
		
		breadcrumbs = (
			('../', u'FAQ'),
			('', category.name)
		)
	else:
		breadcrumbs = (
			('', u'FAQ'),
		)
		
		topics = Topic.objects.all()
	
	return TemplateResponse(
		request,
		category and 'faq/category.html' or 'faq/topics.html',
		{
			'category': category,
			'categories': Category.objects.filter(topics__isnull = False).distinct(),
			'topics': topics,
			'breadcrumb_trail': breadcrumbs,
			'menu_selection': 'faq',
			'body_casses': ('faq',)
		}
	)