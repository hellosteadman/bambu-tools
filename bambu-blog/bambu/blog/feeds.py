from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed
from django.contrib.sites.models import Site
from django.conf import settings
from django.template import Template, Context
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from bambu.blog.models import Category
from bambu.blog.helpers import view_filter, title_parts

POSTS_PER_PAGE = getattr(settings, 'BLOG_POSTS_PER_PAGE', 10)

class ContentFeed(Rss201rev2Feed):
	def root_attributes(self):
		attrs = super(ContentFeed, self).root_attributes()
		attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
		return attrs
	
	def add_item_elements(self, handler, item):
		super(ContentFeed, self).add_item_elements(handler, item)
		
		handler.startElement('content:encoded', {})
		handler._write('<![CDATA[%s]]>' % item['content_encoded'])
		handler.endElement('content:encoded')

class BlogFeed(Feed):
	feed_type = ContentFeed
	
	def items(self, obj):
		posts = view_filter(**obj).live()
		paginator = Paginator(posts, POSTS_PER_PAGE)
		
		try:
			posts = paginator.page(self.page)
		except PageNotAnInteger:
			posts = paginator.page(1)
		except EmptyPage:
			posts = paginator.page(paginator.num_pages)
		
		return posts.object_list
	
	def get_object(self, request, **kwargs):
		self.page = request.GET.get('page')
		return kwargs
	
	def link(self):
		site = Site.objects.get_current()
		return 'http://%s/' % (site.domain)
	
	def title(self, obj):
		site = Site.objects.get_current()
		parts = title_parts(**obj)
		parts.append(site.name)
		parts.reverse()
		
		return ': '.join(parts)
	
	def categories(self):
		return Category.objects.filter(
			posts__isnull = False
		).distinct().values_list('name', flat = True)
	
	def item_title(self, item):
		return item.title
	
	def item_description(self, item):
		return item.excerpt
	
	def item_enclosure_url(self, item):
		enclosures = item.attachments.filter(
			mimetype__in = (
				'video/avi',
				'video/msvideo',
				'video/x-msvideo',
				'audio/mpeg3',
				'audio/x-mpeg-3',
				'video/mp4',
				'video/x-m4v',
				'video/mpeg'
			)
		)
		
		if enclosures.count() == 1:
			enclosure = enclosures[0]
			url = enclosure.file.url
			q = url.find('?')
			if q > -1:
				url = url[:q]
			
			return url.replace('https://', 'http://')
	
	def item_enclosure_length(self, item):
		enclosures = item.attachments.filter(
			mimetype__in = (
				'video/avi',
				'video/msvideo',
				'video/x-msvideo',
				'audio/mpeg3',
				'audio/x-mpeg-3',
				'video/x-m4v',
				'video/mp4',
				'video/mpeg'
			)
		)
		
		if enclosures.count() == 1:
			return enclosures[0].size
	
	def item_enclosure_mime_type(self, item):
		enclosures = item.attachments.filter(
			mimetype__in = (
				'video/avi',
				'video/msvideo',
				'video/x-msvideo',
				'audio/mpeg3',
				'audio/x-mpeg-3',
				'audio/x-wav',
				'video/x-m4v',
				'video/mp4',
				'video/mpeg'
			)
		)
		
		if enclosures.count() == 1:
			return enclosures[0].mimetype
	
	def item_pubdate(self, item):
		return item.date
	
	def item_author_name(self, item):
		return item.author.get_full_name() or item.author.username
	
	def item_author_email(self, item):
		return item.author.email
	
	def item_categories(self, item):
		return item.categories.values_list('name', flat = True)
	
	# def item_copyright(self, item):
	# 		return item.channel.copyright
	
	# def item_subtitle(self, item):
	# 		return item.subtitle
	
	def item_extra_kwargs(self, item):
		kwargs = super(BlogFeed, self).item_extra_kwargs(item)
		kwargs['content_encoded'] = ' '.join(
			Template(
				'{% load markup oembed attachments %}' \
				'{{ post.body|markdown|oembed|attachments:post }}'
			).render(
				Context(
					{
						'post': item,
					}
				)
			).splitlines()
		)
		
		return kwargs