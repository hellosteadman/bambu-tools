from django.db import transaction
from django.contrib.auth import authenticate
from django.contrib.sites.models import Site
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.core.files import File
from bambu.xmlrpc import handler, XMLRPCException
from bambu.blog.models import Post, Category, PostUpload
from tempfile import mkstemp
from logging import getLogger
from pyquery import PyQuery
from os import path, close, write

STAFF_ONLY = getattr(settings, 'BLOG_XMLRPC_STAFF_ONLY', True)
LOGGER = getLogger('bambu.blog')

def clean_body(body):
	site = Site.objects.get_current()
	html = PyQuery('<body>' + body + '</body>')
	
	for p in html('p'):
		p = PyQuery(p)
		p.replaceWith('\n\n%s\n\n' % p.html())
	
	html('.alignright').addClass('pull-right').removeClass('alignright')
	html('.alignleft').addClass('pull-left').removeClass('alignleft')
	html('[style="float: left;"]').removeAttr('style').addClass('alignleft')
	html('[style="float: right;"]').removeAttr('style').addClass('alignright')
	
	while '\n\n\n' in body:
		body = body.replace('\n\n\n', '\n\n')
	
	while '\r\r\r' in body:
		body = body.replace('\r\r\r', '\r\r')
	
	body = html.html()
	body = body.replace('<br />', '  \n')
	body = body.replace('<br/>', '  \n')
	body = body.replace('<br>', '  \n')
	body = body.replace('\r\n', '\n')
	body = body.replace('\n\r', '\n')
	
	while body.find('\n\n\n') > -1:
		body = body.replace('\n\n\n', '\n\n')
	
	while body.startswith('\n'):
		body = body[1:]
	
	while body.endswith('\n'):
		body = body[:-1]
	
	while body.startswith('\r'):
		body = body[1:]
	
	while body.endswith('\r'):
		body = body[:-1]
	
	while body.startswith('\t'):
		body = body[1:]
	
	return body

def get_attachments(body):
	if body:
		html = PyQuery('<body>' + body + '</body>')
		
		for a in html('[src], [href]'):
			a = PyQuery(a)
			if a.attr('href'):
				url = a.attr('href')
			else:
				url = a.attr('src')
			
			try:
				upload = PostUpload.objects.get(url__iexact = url)
			except PostUpload.DoesNotExist:
				continue
			
			yield upload

def auth(username, password, *perms):
	user = authenticate(username = username, password = password)
	if not user:
		raise XMLRPCException('Login failed.', code = 401)
	
	if not user.is_active:
		raise XMLRPCException('User is inactive.', code = 401)
	
	if STAFF_ONLY and not user.is_staff:
		raise XMLRPCException('User is not a member of staff.', code = 401)
	
	if any(perms) and not user.has_perms(perms):
		raise XMLRPCException('User does not have permission to perform this action.', code = 401)
	
	return user

@handler('metaWeblog.getPost')
def get_post(postid, username, password):
	user = auth(username, password)
	site = Site.objects.get_current()
	
	try:
		post = Post.objects.get(pk = postid, author = user)
	except Post.DoesNotExist:
		raise XMLRPCException('Post not found.', code = 404)
	
	ret = {
		'postid': post.pk,
		'title': post.title or u'',
		'description': post.body or u'',
		'link': 'http://%s%s' % (site.domain, post.get_absolute_url()),
		'userid': post.author.username,
		'dateCreated': post.date,
		'categories': [
			c for c in post.categories.exclude(name = '').exclude(name = None).values_list(
				'name', flat = True
			)
		],
		'mt_keywords': ', '.join(
			[
				t for t in post.tags.exclude(name = '').exclude(name = None).values_list(
					'name', flat = True
				)
			]
		),
		'wp_slug': post.slug,
		'post_status': post.published and 'publish' or 'draft'
	}
	
	enclosures = post.attachments.filter(
		mimetype__in = (
			'video/avi',
			'video/msvideo',
			'video/x-msvideo',
			'audio/mpeg3',
			'audio/x-mpeg-3',
			'audio/x-wav',
			'video/mp4',
			'video/x-m4v',
			'video/mpeg'
		)
	)
	
	if enclosures.exists():
		enclosure = enclosures[0]
		
		ret['enclosure'] = {
			'url': enclosure.file.url,
			'length': enclosure.file.size,
			'type': enclosure.mimetype
		}
	
	return ret

@handler('metaWeblog.getRecentPosts')
def get_posts(blogid, username, password, numberOfPosts = 10):
	user = auth(username, password)
	site = Site.objects.get_current()
	
	if numberOfPosts > 10:
		numberOfPosts = 10
	
	posts = []
	for post in Post.objects.filter(author = user)[:numberOfPosts]:
		posts.append(
			{
				'postid': post.pk,
				'title': post.title or u'',
				'description': post.body or u'',
				'link': 'http://%s%s' % (site.domain, post.get_absolute_url()),
				'userid': post.author.username,
				'dateCreated': post.date,
				'categories': [
					n for n in post.categories.exclude(name = '').exclude(name = None).values_list(
						'name', flat = True
					)
				],
				'mt_keywords': ', '.join(
					[
						t for t in post.tags.exclude(name = '').exclude(name = None).values_list(
							'name', flat = True
						)
					]
				),
				'wp_slug': post.slug,
				'post_status': post.published and 'publish' or 'draft'
			}
		)
	
	return posts

@handler('metaWeblog.newPost')
@transaction.commit_on_success
def new_post(blogid, username, password, content, publish):
	user = auth(username, password, 'blog.create_posts')
	
	uploads = get_attachments(content.get('description'))
	post = Post.objects.create(
		author = user,
		title = content.get('title'),
		body = clean_body(content.get('description', '')),
		date = content.get('dateCreated', now()),
		slug = content.get('wp_slug', slugify(content.get('title'))) or None,
		published = publish
	)
	
	for upload in uploads:
		upload.convert_to_attachment(post)
	
	for name in content.get('categories', []):
		slug = slugify(name)
		
		try:
			category = Category.objects.get(slug = slug)
		except Category.DoesNotExist:
			category = Category.objects.create(
				name = name,
				slug = slug
			)
		
		post.categories.add(category)
	
	for tag in [t.strip() for t in content.get('mt_keywords', '').split(', ')]:
		if tag:
			post.tags.add(tag)
	
	return str(post.pk)

@handler('metaWeblog.editPost')
@transaction.commit_on_success
def edit_post(postid, username, password, content, publish):
	user = auth(username, password, 'blog.change_posts')
	uploads = get_attachments(content.get('description'))
	
	try:
		post = Post.objects.get(pk = postid)
	except Post.DoesNotExist:
		raise XMLRPCException('Post not found.', code = 404)
	
	if post.author.pk != user.pk:
		raise XMLRPCException('Only the authoe can edit this post.', code = 401)
	
	post.title = content.get('title', post.title)
	
	if 'description' in content:
		post.body = clean_body(content['description'] or u'')
	
	post.date = content.get('dateCreated', post.date)
	post.slug = content.get('wp_slug', post.slug)
	post.published = publish
	post.save()
	
	for upload in uploads:
		upload.convert_to_attachment(post)
	
	if content.has_key('categories'):
		slugs = []
		for name in content['categories']:
			slug = slugify(name)
			if not slug:
				continue
			
			try:
				category = Category.objects.get(slug = slug)
			except Category.DoesNotExist:
				category = Category.objects.create(
					name = name,
					slug = slug
				)
			
			post.categories.add(category)
			slugs.append(category.slug)
		
		for pk in post.categories.exclude(slug__in = slugs).values_list('pk', flat = True):
			post.categories.remove(pk)
	
	if content.get('mt_keywords'):
		added_tags = []
		for tag in [t.strip() for t in content['mt_keywords'].split(', ')]:
			if tag.startswith('"') and tag.endswith('"'):
				tag = tag[1:-1]
			elif tag.startswith("'") and tag.endswith("'"):
				tag = tag[1:-1]
			
			if tag:
				post.tags.add(tag)
				added_tags.append(tag)
		
		for pk in post.tags.exclude(name__in = added_tags).values_list('pk', flat = True):
			post.tags.remove(pk)
	
	return True

@handler('metaWeblog.newMediaObject')
@transaction.commit_on_success
def upload_media(blogid, username, password, data):
	if not data.has_key('bits'):
		raise XMLRPCException('No data supplied for attachment.')
	
	handle, filename = mkstemp(
		data.get('name') and path.splitext(data['name'])[-1]
	)
	
	write(handle, data['bits'].data)
	close(handle)
	
	upload = PostUpload.objects.create(
		file = File(open(filename, 'r')),
		mimetype = data.get('type')
	)
	
	upload.url = upload.file.url
	upload.save()
	
	return {
		'id': upload.pk,
		'file': upload.file.name,
		'url': upload.url,
		'type': upload.mimetype
	}

@handler('metaWeblog.deletePost')
@handler('blogger.deletePost')
@transaction.commit_on_success
def delete_post(appkey, postid, username, password, publish):
	user = auth(username, password, 'blog.delete_posts')
	
	try:
		post = Post.objects.get(pk = postid)
	except Post.DoesNotExist:
		raise XMLRPCException('Post not found.', code = 404)
	
	if post.author.pk != user.pk:
		raise XMLRPCException('Only the authoe can delete this post.', code = 401)
	
	post.delete()
	return True

@handler('metaWeblog.getCategories')
def get_categories(blogid, username, password):
	user = auth(username, password)
	site = Site.objects.get_current()
	
	return [
		{
			'categoryId': category.pk,
			'parentId': 0,
			'categoryName': category.name,
			'categoryDescription': u'',
			'description': category.name,
			'htmlUrl': 'http://%s%s' % (site.domain,
				reverse('blog_posts_by_category', args = [category.slug])
			),
			'rssUrl': 'http://%s%s' % (site.domain,
				reverse('blog_posts_by_category_feed', args = [category.slug])
			)
		} for category in Category.objects.all()
	]

@handler('metaWeblog.getUsersBlogs')
@handler('blogger.getUsersBlogs')
def get_blogs(appkey, username, password):
	user = auth(username, password)
	site = Site.objects.get_current()
	
	return [
		{
			'blogid': 1,
			'url': 'http://%s%s' % (site.domain, reverse('blog_posts')),
			'blogName': site.name,
			'isAdmin': user.is_staff,
			'xmlrpc': 'http://%s%s' % (site.domain, reverse('xmlrpc_server'))
		}
	]

@handler('blogger.getUserInfo')
def get_blogs(appkey, username, password):
	user = auth(username, password)
	site = Site.objects.get_current()
	
	return {
		'userid': user.pk,
		'nickname': user.username,
		'firstname': user.first_name,
		'lastname': user.last_name,
		'url': 'http://%s%s' % (site.domain,
			reverse('blog_posts_by_author', args = [user.username])
		)
	}