from django.db.models import Count, F
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.utils.timezone import get_current_timezone, now as rightnow
from taggit.models import Tag
from datetime import datetime
from bambu.blog.models import Post, Category
from bambu.blog.helpers import view_filter, title_parts, get_comments_form
from bambu.enqueue import enqueue_css_block

POSTS_PER_PAGE = getattr(settings, 'BLOG_POSTS_PER_PAGE', 10)
THUMBNAIL_WIDTH = getattr(settings, 'BLOG_THUMBNAIL_WIDTH',
	getattr(settings, 'OEMBED_WIDTH', 640)
)

COMMENTS_FORM_CLASS = get_comments_form()

def _context(request):
	def categories():
		return Category.objects.filter(
			posts__pk__in = Post.objects.live().values_list('pk', flat = True)
		).annotate(
			post_count = Count('posts')
		)
	
	def dates():
		return Post.objects.live().dates('date', 'month').reverse()
	
	return {
		'categories': categories,
		'dates': dates,
		'menu_selection': 'blog',
		'THUMBNAIL_WIDTH': unicode(THUMBNAIL_WIDTH)
	}

def posts(request, **kwargs):
	templates = ['blog/posts.html']
	context = _context(request)
	breadcrumb_trail = []
	
	if 'year' in kwargs:
		if 'month' in kwargs:
			if 'day' in kwargs:
				date = datetime(
					int(kwargs['year']),
					int(kwargs['month']),
					int(kwargs['day'])
				).replace(
					tzinfo = get_current_timezone()
				)
				
				context['day'] = date.strftime('%B %d, %Y')
				
				breadcrumb_trail = (
					('../../../', u'Blog'),
					('../../', date.strftime('%Y')),
					('../', date.strftime('%B')),
					('', date.strftime('%d'))
				)
				
				templates.insert(0, 'blog/posts-day.html')
			else:
				date = datetime(
					int(kwargs['year']),
					int(kwargs['month']),
					1
				).replace(
					tzinfo = get_current_timezone()
				)
				
				context['month'] = date.strftime('%B %Y')
				
				breadcrumb_trail = (
					('../../', u'Blog'),
					('../', date.strftime('%Y')),
					('', date.strftime('%B'))
				)
				
				templates.insert(0, 'blog/posts-month.html')
		else:
			context['year'] = kwargs['year']
			templates.insert(0, 'blog/posts-year.html')
			
			breadcrumb_trail = (
				('../', u'Blog'),
				('', int(kwargs['year'])),
			)
	else:
		breadcrumb_trail = (
			('', u'Blog'),
		)
	
	if 'category' in kwargs:
		category = get_object_or_404(Category, slug = kwargs['category'])
		context['category'] = category
		templates.insert(0, 'blog/posts-category.html')
		breadcrumb_trail = (
			('../', u'Blog'),
			('', category.name)
		)
	elif 'tag' in kwargs:
		tag = get_object_or_404(Tag, slug = kwargs['tag'])
		context['tag'] = tag
		templates.insert(0, 'blog/posts-tag.html')
		breadcrumb_trail = (
			('../', u'Blog'),
			('', tag.name)
		)
	elif 'username' in kwargs:
		author = get_object_or_404(User, username = kwargs['username'])
		context['author'] = author
		templates.insert(0, 'blog/posts-author.html')
		breadcrumb_trail = (
			('../', u'Blog'),
			('', author.get_full_name() or author.username)
		)
	
	posts = view_filter(**kwargs)
	paginator = Paginator(posts, POSTS_PER_PAGE)
	page = request.GET.get('page')
	
	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		posts = paginator.page(1)
	except EmptyPage:
		posts = paginator.page(paginator.num_pages)
	
	context['page'] = posts
	context['breadcrumb_trail'] = breadcrumb_trail
	context['title_parts'] = title_parts(**kwargs)
	
	context['enqueued_styles'] = [
		enqueue_css_block(request, posts.object_list.css(True))
	]
	
	return TemplateResponse(
		request,
		templates,
		context
	)

def post(request, year, month, day, slug):
	preview = False
	kwargs = {
		'date__year': int(year),
		'date__month': int(month),
		'date__day': int(day),
		'slug': slug
	}
	
	now = rightnow()
	if not request.user.is_staff:
		kwargs['date__lte'] = now
		kwargs['published'] = True
	
	try:
		post = Post.objects.select_related().get(**kwargs)
	except:
		raise Http404('No Post matches the given query.')
	
	if not post.published or post.date > now:
		preview = True
	
	context = _context(request)
	context['post'] = post
	context['day'] = post.date.strftime('%B %d, %Y')
	context['breadcrumb_trail'] = (
		('../../../../', u'Blog'),
		('../../../', post.date.strftime('%Y')),
		('../../', post.date.strftime('%B')),
		('../', post.date.strftime('%d')),
		('', unicode(post))
	)
	
	context['title_parts'] = (unicode(post), u'Blog')
	context['newer_posts'] = Post.objects.filter(date__gt = post.date).live()
	context['older_posts'] = Post.objects.filter(date__lt = post.date).live()
	
	if not request.GET.get('comment-sent'):
		initial = {}
		
		if request.user.is_authenticated():
			initial = {
				'name': request.user.get_full_name() or request.user.username,
				'email': request.user.email,
				'website': 'http://%s/' % Site.objects.get_current().domain
			}
		
		context['comment_form'] = COMMENTS_FORM_CLASS(initial = initial)
	
	context['body_classes'] = ['post-%s' % post.pk, 'post-%s' % post.slug]
	if preview:
		context['body_classes'].append('post-preview')
		context['preview'] = True
	
	if post.css:
		context['enqueued_styles'] = [
			enqueue_css_block(request, post.render_css)
		]
		
		context['body_classes'].append('post-custom-css')
	
	return TemplateResponse(
		request,
		'blog/post.html',
		context
	)

@require_POST
def post_comment(request, year, month, day, slug):
	try:
		post = Post.objects.live().select_related().get(
			date__year = int(year),
			date__month = int(month),
			date__day = int(day),
			slug = slug
		)
	except Post.DoesNotExist:
		raise Http404('Post not found.')
	
	form = COMMENTS_FORM_CLASS(request.POST)
	if request.POST.get('h0n3ytr4p'):
		return HttpResponse('')
	
	if form.is_valid():
		comment = form.save(commit = False)
		with transaction.commit_on_success():
			if request.POST.get('content_type'):
				comment.content_type = ContentType.objects.get(
					pk = int(request.POST['content_type'])
				)
			else:
				comment.content_type = ContentType.objects.get_for_model(post)
			
			if request.POST.get('object_id'):
				comment.object_id = comment.content_type.get_object_for_this_type(
					pk = int(request.POST['object_id'])
				).pk
			else:
				comment.object_id = post.pk
			
			comment.spam = comment.check_for_spam(request)
			comment.save()
			
			messages.add_message(
				request,
				messages.SUCCESS,
				u'Your comment has been submitted successfully.'
			)
			
			return HttpResponseRedirect(
				'%s?comment-sent=true' % post.get_absolute_url()
			)
	
	context = _context(request)
	context['post'] = post
	context['day'] = post.date.strftime('%B %d, %Y')
	context['newer_posts'] = Post.objects.filter(date__gt = post.date).live()
	context['older_posts'] = Post.objects.filter(date__lt = post.date).live()
	context['breadcrumb_trail'] = (
		('../../../../../', u'Blog'),
		('../../../../', post.date.strftime('%Y')),
		('../../../', post.date.strftime('%B')),
		('../../', post.date.strftime('%d')),
		('../', unicode(post)),
		('', u'Post comment')
	)
	
	context['title_parts'] = (unicode(post), u'Blog')
	context['comment_form'] = form
	context['comment_form_action'] = '.'
	context['body_classes'] = ['post-%s' % post.pk, 'post-%s' % post.slug]
	
	if post.css:
		context['enqueued_styles'] = [
			enqueue_css_block(request, post.css)
		]
		
		context['body_classes'].append('post-custom-css')
	
	return TemplateResponse(
		request,
		'blog/post.html',
		context
	)