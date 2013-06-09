from django.contrib import admin
from django.views.decorators.http import require_POST
from django.forms.formsets import all_valid
from django.contrib.admin.util import unquote
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from bambu.preview.models import Preview

class PreviewableModelAdmin(admin.ModelAdmin):
	add_form_template = 'admin/preview/change_form.html'
	change_form_template = 'admin/preview/change_form.html'
	
	def get_urls(self):
		from django.conf.urls import patterns, url
		
		info = self.model._meta.app_label, self.model._meta.module_name
		urlpatterns = patterns('',
			url(r'^add/preview/$',
				require_POST(self.admin_site.admin_view(self.preview_view)),
				name = '%s_%s_preview' % info
			),
			url(r'^(.+)/preview/$',
				require_POST(self.admin_site.admin_view(self.preview_view)),
				name = '%s_%s_preview' % info
			)
		)
		
		return urlpatterns + super(PreviewableModelAdmin, self).get_urls()
	
	def preview_view(self, request, object_id = None, extra_context = None):
		from django.utils import simplejson
		
		if object_id:
			obj = self.get_object(request, unquote(object_id))
		else:
			obj = self.model()
		
		ModelForm = self.get_form(request, obj)
		form = ModelForm(request.POST, request.FILES, instance = obj)
		opts = self.model._meta
		
		if form.is_valid():
			obj = form.save(commit = False)
		else:
			return TemplateResponse(
				request,
				'preview/error.html',
				{
					'opts': opts,
					'errors': form.errors
				}
			)
		
		prefixes = {}
		formsets = []
		
		if hasattr(self, 'inline_instances'):
			for FormSet, inline in zip(self.get_formsets(request), self.inline_instances):
				prefix = FormSet.get_default_prefix()
				prefixes[prefix] = prefixes.get(prefix, 0) + 1
			
				if prefixes[prefix] != 1:
					prefix = "%s-%s" % (prefix, prefixes[prefix])
			
				formset = FormSet(
					data = request.POST, files = request.FILES,
					instance = obj, prefix = prefix,
					queryset = inline.queryset(request)
				)
			
				formsets.append(formset)
			
			if not all_valid(formsets) and form_validated:
				errors = ''
				for (i, formset) in enumerate(formsets):
					if formset.errors:
						errors += '<li>Formset %d%s</li>' % ((i + 1), formset.errors)
				
				return TemplateResponse(
					request,
					'preview/error.html',
					{
						'opts': opts,
						'errors': errors
					}
				)
			
			inline_data = []
			if len(formset.forms) > 0:
				cleaned_data = []
				for subform in formset.forms:
					cleaned_dict = subform.cleaned_data
					cleaned_dict.update(subform.files)
					cleaned_data.append(cleaned_dict)
			
				inline_data.append(
					(formset.model, cleaned_data)
				)
		else:
			inline_data = []
		
		Preview.objects.clear_for_model(self.model, request.user)
		preview = Preview.objects.create_preview(
			model = self.model,
			title = unicode(obj),
			data = dict(form.cleaned_data),
			user = request.user,
			inline_data = inline_data
		)
		
		return HttpResponseRedirect(
			preview.get_absolute_url()
		)