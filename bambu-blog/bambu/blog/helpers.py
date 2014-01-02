from django.contrib.auth.models import User
from django.utils.timezone import get_current_timezone
from django.utils.importlib import import_module
from django.conf import settings
from taggit.models import Tag
from datetime import datetime

def view_filter(**kwargs):
	from bambu.blog.models import Post, Category
	posts = Post.objects.select_related().live()
	
	if 'year' in kwargs:
		posts = posts.filter(
			date__year = int(kwargs['year'])
		)
		
		if 'month' in kwargs:
			posts = posts.filter(
				date__month = int(kwargs['month'])
			)
			
			if 'day' in kwargs:
				posts = posts.filter(
					date__day = int(kwargs['day'])
				)
	
	if 'category' in kwargs:
		posts = posts.filter(categories__slug = kwargs['category'])
	elif 'tag' in kwargs:
		posts = posts.filter(tags__slug = kwargs['tag'])
	elif 'username' in kwargs:
		posts = posts.filter(author__username = kwargs['username'])
	
	return posts
	
def title_parts(**kwargs):
	from bambu.blog.models import Category
	
	title_parts = [u'Blog']
	if 'year' in kwargs:
		if 'month' in kwargs:
			if 'day' in kwargs:
				title_parts.insert(0,
					datetime(
						int(kwargs['year']),
						int(kwargs['month']),
						int(kwargs['day'])
					).replace(tzinfo = get_current_timezone()).strftime('%B %d, %Y')
				)
			else:
				title_parts.insert(0,
					datetime(
						int(kwargs['year']),
						int(kwargs['month']),
						1
					).replace(tzinfo = get_current_timezone()).strftime('%B %Y')
				)
		else:
			title_parts.insert(0, kwargs['year'])
	
	if 'category' in kwargs:
		category = Category.objects.get(slug = kwargs['category'])
		title_parts.insert(0, category.name)
	elif 'tag' in kwargs:
		tag = Tag.objects.get(slug = kwargs['tag'])
		title_parts.insert(0, tag.name)
	elif 'username' in kwargs:
		author = User.objects.get(username = kwargs['username'])
		title_parts.insert(0, author.get_full_name() or author.username)
	
	return title_parts
	
def get_post_image(post):
	image_types = (
		'image/bmp', 'image/x-windows-bmp', 'image/gif',
		'image/jpeg', 'image/pjpeg', 'image/png', 'image/tiff'
	)
	
	images = post.attachments.filter(mimetype__in = image_types)[:1]
	if images.exists():
		try:
			url = images[0].file.url
			if url.startswith('/'):
				url = settings.MEDIA_URL[:-1] + url
			
			return url
		except:
			pass
	
	return ''

def get_comments_form():
	klass = getattr(settings, 'BLOG_COMMENTS_FORM',
		'bambu.comments.forms.CommentForm'
	)
	
	module, dot, klass = klass.rpartition('.')
	module = import_module(module)
	klass = getattr(module, klass)
	
	return klass