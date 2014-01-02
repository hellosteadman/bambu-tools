from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.timezone import get_current_timezone
from django.template.defaultfilters import slugify
from django.db import transaction
from django.core.files import File
from bambu.blog.models import Post, Category
from bambu.comments.models import Comment
from bambu.attachments.models import Attachment
from optparse import make_option
from os import sys, path, write, close, remove
from elementtree import ElementTree
from datetime import datetime
from urlparse import urlparse
from tempfile import mkstemp
from pyquery import PyQuery
from lxml import etree
import requests

XML_NS = {
	'wp': 'http://wordpress.org/export/1.2/',
	'content': 'http://purl.org/rss/1.0/modules/content/',
	'dc': 'http://purl.org/dc/elements/1.1/'
}

class Command(BaseCommand):
	help = 'Import blog posts from a WordPress XML file'
	args = '<filename>'
	
	def handle(self, *args, **options):
		xml = ElementTree.parse(open(args[0], 'r'))
		channel = xml.find('channel')
		
		def node_text(node, namespace = None, parent = None):
			if namespace:
				item = (parent or channel).find(ns(namespace, node))
			else:
				item = (parent or channel).find(node)
			
			if not item is None:
				return item.text
			
			return None
		
		def ns(n, o):
			return '{%s}%s' % (XML_NS[n], o)
		
		if channel is None:
			raise CommandError('Cannot find <channel> tag')
		
		title = node_text('title')
		if title:
			print(u'Blog title: %s' % title)
		
		link = node_text('link')
		if link:
			print(u'Blog URL: %s' % link)
		
		description = node_text('description')
		if description:
			print(u'Blog description: %s' % description)
		
		mappings = {
			'users': {},
			'posts': {},
			'categories': {},
			'comments': {}
		}
		
		content_type = ContentType.objects.get_for_model(Post)
		site = Site.objects.get_current()
		postmeta = {}
		
		print
		with transaction.commit_manually():
			try:
				for author in channel.findall(ns('wp', 'wp_author')):
					username = node_text('author_login', 'wp', author)
					email = node_text('author_email', 'wp', author)
					display_name = node_text('author_display_name', 'wp', author)
					user = None
					
					if not username:
						continue
					
					if display_name:
						display_name = '%s (%s)' % (username, display_name)
					else:
						display_name = username
					
					try:
						user = User.objects.get(username__iexact = username)
					except User.DoesNotExist:
						if email:
							try:
								user = User.objects.get(email__iexact = email)
							except:
								pass
					
					if not user:
						new_username = raw_input('Map old user %s to a user in your database: ' % display_name)
						if not new_username:
							continue
						
						while True:
							try:
								user = User.objects.get(username__iexact = new_username)
								break
							except User.DoesNotExist:
								new_username = raw_input('User not found. Please try again ,or press Enter to ignore: ')
								if not new_username:
									print 'Ignoring user %s' % username
									break
					
					if user:
						mappings['users'][username] = user
						print 'Mapping user %s to %s' % (
							username, user.get_full_name() or user.username
						)
				
				for item in channel.findall('item'):
					id = node_text('post_id', 'wp', item)
					title = node_text('title', parent = item)
					url = node_text('link', parent = item)
					kind = node_text('post_type', 'wp', item)
					parent = node_text('post_parent', 'wp', item)
					published = node_text('status', 'wp', item) == 'publish'
					author = node_text('creator', 'dc', item)
					date = node_text('post_date_gmt', 'wp', item)
					body = node_text('encoded', 'content', item) or u''
					
					try:
						id = int(id)
					except ValueError:
						continue
					
					if not date:
						continue
					
					try:
						date = datetime.strptime(date,
							'%Y-%m-%d %H:%M:%S'
						).replace(
							tzinfo = get_current_timezone()
						)
					except:
						continue
					
					try:
						parent = int(parent)
					except ValueError:
						continue
					
					if parent:
						continue
					
					if not author:
						continue
					
					if not mappings['users'].has_key(author):
						continue
					
					author = mappings['users'][author]
					if not kind in ('post', 'page'):
						continue
					
					if kind == 'post':
						try:
							post = Post.objects.get(title = title, date = date)
							print 'Updating %s "%s"' % (kind, title)
						except Post.DoesNotExist:
							post = Post(
								title = title,
								slug = title and slugify(title) or None,
								date = date,
								published = published,
								broadcast = True,
								author = author
							)
							
							print 'Creating %s "%s"' % (kind, title)
					else:
						continue
					
					post.body = body
					post.save()
					mappings['posts'][id] = post
					
					for category in item.findall('category'):
						domain = category.get('domain')
						slug = category.get('nicename')
						
						if not category.text:
							continue
						
						if domain == 'category':
							if not mappings['categories'].has_key(slug):
								mappings['categories'][slug], created = Category.objects.get_or_create(
									name = category.text,
									slug = slugify(category.text)
								)
								
								if created:
									print '- Created category "%s"' % category.text
							
							post.categories.add(
								mappings['categories'][slug]
							)
						elif domain == 'post_tag':
							if category.text.startswith('"') and category.text.endswith('"'):
								post.tags.add(category.text[1:-1])
							else:
								post.tags.add(category.text)
					
					for comment in item.findall(ns('wp', 'comment')):
						comment_id = node_text('comment_id', 'wp', comment)
						comment_name = node_text('comment_author', 'wp', comment)
						comment_email = node_text('comment_author_email', 'wp', comment)
						comment_url = node_text('comment_author_url', 'wp', comment)
						comment_date = node_text('comment_date_gmt', 'wp', comment)
						comment_type = node_text('comment_type', 'wp', comment)
						comment_body = node_text('comment_content', 'wp', comment)
						comment_parent = node_text('comment_parent', 'wp', comment)
						comment_approved = node_text('comment_approved', 'wp', comment) == '1'
						
						try:
							comment_id = int(comment_id)
						except ValueError:
							continue
						
						try:
							comment_parent = int(comment_parent)
						except ValueError:
							comment_parent = 0
						
						try:
							comment_date = datetime.strptime(
								comment_date, '%Y-%m-%d %H:%M:%S'
							).replace(
								tzinfo = get_current_timezone()
							)
						except:
							continue
						
						if not comment_name:
							continue
						
						if not comment_type or comment_type == 'comment':
							try:
								comment = post.comments.get(
									name = comment_name,
									sent = comment_date
								)
							except Comment.DoesNotExist:
								comment = Comment(
									name = comment_name,
									website = comment_url,
									email = comment_email or '',
									sent = comment_date,
									approved = comment_approved,
									body = comment_body,
									content_type = content_type,
									object_id = post.pk
								)
								
								print '- Comment by %s' % comment_name
							
							comment.save(notify = False)
							mappings['comments'][comment_id] = comment
					
					postmeta[id] = {}
					for meta in item.findall(ns('wp', 'postmeta')):
						meta_key = node_text('meta_key', 'wp', meta)
						meta_value = node_text('meta_value', 'wp', meta)
						postmeta[id][meta_key] = meta_value
					
					ai = 1
					for subitem in channel.findall('item'):
						subid = node_text('post_id', 'wp', subitem)
						subparent_id = node_text('post_parent', 'wp', subitem)
						subtitle = node_text('title', parent = subitem)
						suburl = node_text('link', parent = subitem)
						subkind = node_text('post_type', 'wp', subitem)
						suburl = node_text('attachment_url', 'wp', subitem)
						
						try:
							subparent_id = int(subparent_id)
						except ValueError:
							continue
						
						if not suburl:
							continue
						
						if subkind != 'attachment' or subparent_id != id:
							continue
						
						s, d, p, a, q, f = urlparse(suburl)
						d, s, filename = p.rpartition('/')
						
						try:
							attachment = post.attachments.get(
								title = subtitle or filename
							)
						except Attachment.DoesNotExist:
							print '- Downloading %s' % filename

							response = requests.get(suburl)
							handle, tmp = mkstemp(
								path.splitext(filename)[-1]
							)

							write(handle, response.content)
							close(handle)
							
							attachment = Attachment(
								title = subtitle or filename,
								file = File(open(tmp, 'r'), name = filename),
								content_type = content_type,
								object_id = post.pk
							)
						
							if '_thumbnail_id' in postmeta[id]:
								if unicode(postmeta[id]['_thumbnail_id']) == unicode(subid):
									attachment.featured = True
						
							attachment.save()
							remove(tmp)
						
						if post.body:
							html = PyQuery('<body>' + post.body + '</body>')
							for a in html(
								'a[href="%(url)s"], [src="%(url)s"]' % {
									'url': suburl
								}
							):
								a = PyQuery(a)
								a.replaceWith('\n\n[attachment %d]\n\n' % ai)
							
							post.body = html.html()
						
						ai += 1
					
					if post.body:
						html = PyQuery('<body>' + post.body + '</body>')
						for a in html('a[href]'):
							href = a.get('href')
							if href.startswith(link):
								href = href.replace(link, 'http://%s' % site.domain)
							
							a = PyQuery(a)
						
						for p in html('p'):
							p = PyQuery(p)
							p.replaceWith('\n\n%s\n\n' % p.html())
						
						html('.alignright').addClass('pull-right').removeClass('alignright')
						html('.alignleft').addClass('pull-left').removeClass('alignleft')
						
						while '\n\n\n' in post.body:
							post.body = post.body.replace('\n\n\n', '\n\n')
						
						while '\r\r\r' in post.body:
							post.body = post.body.replace('\r\r\r', '\r\r')
						
						post.body = html.html()
						post.body = post.body.replace('<br />', '  \n')
						post.body = post.body.replace('<br/>', '  \n')
						post.body = post.body.replace('<br>', '  \n')
						
						while post.body.startswith('\n'):
							post.body = post.body[1:]
						
						while post.body.endswith('\n'):
							post.body = post.body[:-1]
						
						while post.body.startswith('\r'):
							post.body = post.body[1:]
						
						while post.body.endswith('\r'):
							post.body = post.body[:-1]
						
						while post.body.startswith('\t'):
							post.body = post.body[1:]
						
						post.body = post.body.strip()
					
					post.save()
				
				transaction.commit()
			except:
				transaction.rollback()
				raise