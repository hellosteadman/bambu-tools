from django.db import models, transaction
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.utils.timezone import now
from django.template import Template, Context
from django.conf import settings
from taggit.managers import TaggableManager
from bambu.blog.managers import *
from bambu.blog import helpers
from bambu.attachments.models import Attachment
from bambu.attachments.helpers import upload_attachment_file
from bambu.preview.models import Preview
from mimetypes import guess_type
from hashlib import md5

if 'bambu.webhooks' in settings.INSTALLED_APPS:
	from bambu import webhooks

COMMENTS_MODEL = getattr(settings, 'BLOG_COMMENTS_MODEL', 'comments.Comment')

class Category(models.Model):
	name = models.CharField(max_length = 100, db_index = True)
	slug = models.SlugField(max_length = 100, unique = True)
	
	def __unicode__(self):
		return self.name
	
	@property
	def post_percent(self):
		count = float(getattr(self, 'post_count', self.posts.live().count()))
		all_count = float(Post.objects.live().count())
		
		return count / all_count * 100.0
	
	class Meta:
		ordering = ('name',)
		verbose_name_plural = 'categories'

class Post(models.Model):
	author = models.ForeignKey('auth.User', related_name = 'blog_posts')
	title = models.CharField(max_length = 100, null = True, blank = True)
	slug = models.SlugField(max_length = 100, db_index = True)
	date = models.DateTimeField(db_index = True)
	published = models.BooleanField(default = True)
	broadcast = models.BooleanField(editable = False)
	body = models.TextField()
	css = models.TextField(null = True, blank = True)
	tags = TaggableManager()
	categories = models.ManyToManyField(Category, related_name = 'posts',
		null = True, blank = True
	)
	
	attachments = generic.GenericRelation(Attachment)
	comments = generic.GenericRelation(COMMENTS_MODEL)
	objects = PostManager()
	
	@models.permalink
	def get_absolute_url(self):
		return (
			'blog_post', (
				str(self.date.year).zfill(4),
				str(self.date.month).zfill(2),
				str(self.date.day).zfill(2),
				self.slug
			)
		)
	
	def __unicode__(self):
		return self.title or u'(Untitled)'
	
	@property
	def excerpt(self):
		for line in self.body.splitlines():
			if not line:
				continue
			
			if line.startswith('http://') or line.startswith('http://'):
				continue
			
			if line.startswith('[') and line.endswith(']'):
				continue

			if line.startswith('#') or line.startswith('>'):
				continue
			
			return line
	
	def next_post(self):
		try:
			return Post.objects.live().filter(date__gt = self.date)[0]
		except:
			pass
	
	def previous_post(self):
		try:
			return Post.objects.live().filter(date__lt = self.date).latest()
		except:
			pass
	
	def render_css(self):
		template = Template(self.css)
		context = Context(
			{
				'attachments': self.attachments.all(),
				'slug': self.slug,
				'pk': self.pk,
				'id': self.pk
			}
		)
		
		return template.render(context)
	
	def featured_attachment(self):
		try:
			return self.attachments.filter(featured = True)[0]
		except IndexError:
			return None
	
	def save(self, *args, **kwargs):
		publish = False
		if self.pk:
			old = Post.objects.get(pk = self.pk)
			if self.published and not old.published:
				publish = True
		elif self.published:
			publish = True
		
		if not self.slug and not self.title:
			slug = str(
				Post.objects.filter(
					date__year = self.date.year,
					date__month = self.date.month,
					date__day = self.date.day
				).count() + 1
			)
			
			while Post.objects.filter(
				date__year = self.date.year,
				date__month = self.date.month,
				date__day = self.date.day,
				slug = slug
			).exists():
				slug = str(int(slug) + 1)
			
			self.slug = slug
		
		super(Post, self).save(*args, **kwargs)
		Preview.objects.clear_for_model(self, self.author)
		
		if publish and self.date <= now():
			self.publish()
	
	def publish(self):
		if 'bambu.webhooks' in settings.INSTALLED_APPS:
			webhooks.send('post_published', self.author,
				{
					'id': self.pk,
					'title': self.title,
					'slug': self.slug,
					'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
					'body': self.body,
					'tags': [t for t in self.tags.values_list('slug', flat = True)],
					'categories': [c for c in self.categories.values_list('slug', flat = True)],
					'attachments': [
						a.file.url for a in self.attachments.all()
					]
				},
				md5('blogpost:%d' % self.pk).hexdigest()
			)
		
		self.broadcast = True
	
	class Meta:
		ordering = ('-date',)
		get_latest_by = 'date'
	
	class QuerySet(models.query.QuerySet):
		def live(self):
			return self.filter(
				date__lte = now(),
				published = True
			)
		
		def css(self, rendered = False):
			if rendered:
				return '\n\n'.join(
					[
						(post.render_css() or u'') for post in self.all()
					]
				)
			else:
				return '\n\n'.join(
					[
						(css or u'') for css in self.values_list('css', flat = True)
					]
				)

class PostUpload(models.Model):
	file = models.FileField(max_length = 255, upload_to = upload_attachment_file)
	url = models.CharField(max_length = 255, db_index = True)
	size = models.PositiveIntegerField(editable = False)
	mimetype = models.CharField(max_length = 50, editable = False, db_index = True)
	
	def __unicode__(self):
		return self.title
	
	def convert_to_attachment(self, post):
		with transaction.commit_on_success():
			attachment = post.attachments.create(
				file = self.file,
				size = self.size,
				mimetype = self.file.size
			)
		
			self.delete()
		
		return attachment
	
	def save(self, *args, **kwargs):
		if self.file and not self.mimetype:
			self.mimetype, encoding = guess_type(self.file.name)
		
		if not self.size:
			self.size = self.file.size
		
		self.url = self.file.url
		super(PostUpload, self).save(*args, **kwargs)
	
	class Meta:
		db_table = 'blog_post_upload'

if 'bambu.webhooks' in settings.INSTALLED_APPS:
	webhooks.site.register('post_published',
		description = 'Fired when a post is published',
		staff_only = True
	)