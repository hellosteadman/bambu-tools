from django import forms
from django.conf import settings
from django.utils.timezone import now
from django.core.files import File
from django.template.defaultfilters import slugify
from bambu.blog.models import Post
from zipfile import ZipFile

class PostForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(PostForm, self).__init__(*args, **kwargs)
		self.fields['date'].initial = now()
		self.fields['tags'].required = False
		
		if 'markitup' in settings.INSTALLED_APPS:
			from markitup.widgets import MarkItUpWidget
			self.fields['body'].widget = MarkItUpWidget()
		
		self.fields['css'].label = u'Custom CSS'
	
	class Meta:
		model = Post

class UploadForm(forms.ModelForm):
	zip = forms.FileField(label = u'Zip file', help_text = u'Upload your blog post')
	markdown = forms.BooleanField(
		label = u'Convert to Markdown',
		help_text = u'Convert post HTML to Markdown for ease-of-editing later',
		initial = True,
		required = False
	)
	
	def __init__(self, *args, **kwargs):
		super(UploadForm, self).__init__(*args, **kwargs)
		self.fields['tags'].required = False
	
	def clean_zip(self):
		try:
			self._zipfile = ZipFile(self.cleaned_data['zip'])
		except:
			raise forms.ValidationError('Upload a valid Zip file.')
		
		try:
			self._html = self._zipfile.read('post.html')
		except:
			raise forms.ValidationError('Zip file must contain at least one file, called post.html.')
	
	def save(self, commit = False):
		from pyquery import PyQuery as pq
		from dateutil import parser
		from tempfile import mkstemp
		from os import path, write, close, remove
		
		post = super(UploadForm, self).save(commit = False)
		post.body = 'Intermediate'
		post.date = now()
		post.published = False
		post.save()
		
		for category in self.cleaned_data.get('categories'):
			post.categories.add(category)
		
		for tag in self.cleaned_data.get('tags'):
			post.tags.add(tag)
		
		try:
			zipfile = self._zipfile
			html = pq(self._html)
			
			title = html('[data-bpfield="title"]').text()
			date = html('[data-bpfield="date"]').text()
			body = html('[data-bpfield="body"]')
			
			attachments = {}
			for img in body('[src]'):
				src = img.get('src')
				
				if not src:
					return
			
				if src.startswith('//') or src.startswith('http://') or src.startswith('https://'):
					continue
			
				try:
					zipped = zipfile.getinfo(src)
				except KeyError:
					continue
				
				handle, temp = mkstemp(path.splitext(src)[-1])
				write(handle, zipfile.open(src).read())
				close(handle)
				
				attachments[src] = 	post.attachments.create(
					file = File(open(temp, 'r')),
					title = src
				).file.url
				
				remove(temp)
				img = pq(img).attr('src', attachments[src])
				if not img.attr('alt'):
					img.attr('alt', src)
			
			post.title = title or '(No title)'
			
			try:
				post.date = parser.parse(date)
			except:
				pass
			
			if self.cleaned_data.get('markdown'):
				from html2text import HTML2Text
				writer = HTML2Text()
				writer.body_width = 0
				post.body = writer.handle(body.html())
			else:
				post.body = body.html().replace('\t', '')
			
			post.slug = slugify(post.title)
			
			css = html('[data-bpfield="css"]').text()
			if css:
				for old, new in attachments.items():
					css = css.replace(
						'(%s)' % old, "('%s')" % new
					).replace(
						"'%s'" % old, "'%s'" % new
					).replace(
						'"%s"' % old, '"%s"' % new
					)
				
				post.css = css
			
			post.save()
			return post
		except:
			post.delete()
			raise
	
	class Meta:
		model  = Post
		exclude = ('title', 'body', 'css', 'date', 'slug')