from haystack import indexes
from bambu.pages.models import Page
from datetime import datetime

class PageIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document = True, use_template = True)

	def get_model(self):
		return Page
