from haystack import indexes, site
from bambu.pages.models import Page
from datetime import datetime

class PageIndex(indexes.SearchIndex):
	text = indexes.CharField(document = True, use_template = True)
	
	def get_model(self):
		return Page

site.register(Page, PageIndex)