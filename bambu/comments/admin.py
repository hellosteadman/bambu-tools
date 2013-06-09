from django.contrib import admin
from bambu.comments.models import Comment

class CommentAdmin(admin.ModelAdmin):
	def mark_spam(self, request, queryset):
		queryset.update(spam = True, approved = False)
	mark_spam.short_description = 'Mark selected comments as spam'
	
	def mark_approved(self, request, queryset):
		queryset.update(spam = False, approved = True)
	mark_approved.short_description = 'Mark selected comments as approved'
	
	list_display = ('__unicode__', 'name', 'email', 'approved', 'spam')
	list_filter = ('approved', 'spam')
	exclude = ('spam', 'content_type', 'object_id')
	date_hierarchy = 'sent'
	readonly_fields = ('sent',)
	actions = (mark_spam, mark_approved)
	
	def changelist_view(self, request, extra_context = None):
		if not request.GET.has_key('spam__exact'):
			q = request.GET.copy()
			q['spam__exact'] = '0'
			request.GET = q
			request.META['QUERY_STRING'] = request.GET.urlencode()
		
		return super(CommentAdmin, self).changelist_view(request, extra_context)

admin.site.register(Comment, CommentAdmin)