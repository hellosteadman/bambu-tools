from haystack import indexes, site
from bambu.comments.models import Comment
from datetime import datetime

class CommentIndex(indexes.SearchIndex):
	text = indexes.CharField(document = True, use_template = True)
	name = indexes.CharField(model_attr = 'name')
	date = indexes.DateTimeField(model_attr = 'sent')
	
	def get_model(self):
		return Comment
	
	def index_queryset(self, using = None):
		return super(CommentIndex, self).index_queryset().filter(approved = True)

site.register(Comment, CommentIndex)