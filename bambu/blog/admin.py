from django.contrib import admin
from django.contrib.admin.helpers import AdminForm, InlineAdminFormSet, AdminErrorList
from django.conf import settings
from django.conf.urls import patterns
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from bambu.blog.models import *
from bambu.blog.forms import PostForm, UploadForm
from bambu.attachments.admin import AttachmentInline
from bambu.preview.admin import PreviewableModelAdmin

class PostAdmin(PreviewableModelAdmin):
	list_display = ('title', 'date', 'published')
	list_filter = ('published', 'categories')
	date_hierarchy = 'date'
	prepopulated_fields = {
		'slug': ('title',)
	}
	
	search_fields = ('title', 'body')
	
	form = PostForm
	fieldsets = (
		(
			u'Basics',
			{
				'fields': ('title', 'date', 'published')
			}
		),
		(
			u'Post content',
			{
				'fields': ('body',)
			}
		),
		(
			u'Metadata',
			{
				'fields': ('slug', 'author', 'tags', 'categories'),
				'classes': ('collapse', 'closed')
			}
		),
		(
			u'Advanced',
			{
				'fields': ('css',)
			}
		)
	)
	
	inlines = (AttachmentInline,)
	
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'author':
			kwargs['initial'] = request.user
		
		return super(PostAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
	
	def get_urls(self):
		urls = patterns('',
			(r'^upload/$', self.admin_site.admin_view(self.upload_view)),
			(r'^boilerplate/$', self.admin_site.admin_view(self.boilerplate_view))
		)
		
		return urls + super(PostAdmin, self).get_urls()
	
	def upload_view(self, request, form_url = '', extra_context = None):
		model = self.model
		opts = model._meta
		
		if not self.has_add_permission(request):
			raise PermissionDenied
		
		formsets = []
		inline_instances = self.get_inline_instances(request)
		if request.method == 'POST':
			form = UploadForm(request.POST, request.FILES)
			if form.is_valid():
				new_object = self.save_form(request, form, change = False)
				form_validated = True
			else:
				form_validated = False
				new_object = self.model()
			
			if form_validated:
				self.save_model(request, new_object, form, False)
				self.log_addition(request, new_object)
				
				return self.response_add(request, new_object)
		else:
			initial = dict(request.GET.items())
			initial['author'] = request.user
			
			for k in initial:
				try:
					f = opts.get_field(k)
				except models.FieldDoesNotExist:
					continue
				
				if isinstance(f, models.ManyToManyField):
					initial[k] = initial[k].split(",")
			
			form = UploadForm(initial = initial)
			prefixes = {}
		
		adminForm = AdminForm(form,
			[
				(None,
					{
						'fields': list(form.base_fields) + list(self.get_readonly_fields(request))
					}
				)
			],
			{},
			self.get_readonly_fields(request),
			model_admin = self
		)
		
		media = self.media + adminForm.media
		context = {
			'title': _('Add %s') % opts.verbose_name,
			'adminform': adminForm,
			'is_popup': "_popup" in request.REQUEST,
			'media': media,
			'inline_admin_formsets': [],
			'errors': AdminErrorList(form, formsets),
			'app_label': opts.app_label,
			'show_delete': False
		}
		
		context.update(extra_context or {})
		return self.render_change_form(
			request,
			context,
			form_url = form_url,
			add = True
		)
	
	def boilerplate_view(self, request):
		from django.template.loader import get_template
		from django.template import Context
		from django.contrib.sites.models import Site
		from django.http import HttpResponse
		
		site = Site.objects.get_current()
		template = get_template('blog/boilerplate.html')
		media_url = getattr(settings, 'MEDIA_URL', '/media/')
		static_url = getattr(settings, 'STATIC_URL', '/static/')
		
		if media_url.startswith('/') and not media_url.startswith('//'):
			media_url = 'http://%s%s' % (site.domain, media_url)
		
		if static_url.startswith('/') and not static_url.startswith('//'):
			static_url = 'http://%s%s' % (site.domain, static_url)
		
		date = now()
		html = template.render(
			Context(
				{
					'post': {
						'title': u'New title',
						'author': request.user,
						'date': date,
						'body': u'<p>Enter the HTML for your post here. Also add any &lt;script&gt; tags you would like to include.</p>'
					},
					'MEDIA_URL': media_url,
					'STATIC_URL': static_url,
					'SITE': site,
					'body_classes': ('blog', 'blog-post'),
					'breadcrumb_trail': (
						('#', u'Blog'),
						('#', date.strftime('%Y')),
						('#', date.strftime('%B')),
						('#', date.strftime('%d')),
						('', u'New title')
					)
				}
			)
		)
		
		response = HttpResponse(html, mimetype = 'text/html')
		response['Content-Disposition'] = 'attachment; filename=post.html'
		
		return response
	
	class Media:
		css = 'bambu.codemirror' in settings.INSTALLED_APPS and {
			'all': ('codemirror/lib/codemirror.css',)
		} or {}
		
		js = 'bambu.codemirror' in settings.INSTALLED_APPS and (
			'codemirror/lib/codemirror.js',
			'codemirror/mode/css/css.js',
			'blog/admin.js'
		) or ()

admin.site.register(Post, PostAdmin)

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)
	prepopulated_fields = {
		'slug': ('name',)
	}

admin.site.register(Category, CategoryAdmin)