from django.contrib.sitemaps import Sitemap
from bambu.blog.models import Post

class BlogSitemap(Sitemap):
	changefreq = 'daily'
	priority = 0.5
	
	def items(self):
		return Post.objects.live()
	
	def lastmod(self, obj):
		return obj.date