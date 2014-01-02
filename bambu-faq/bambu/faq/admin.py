from django.contrib import admin
from bambu.faq.models import Category, Topic

class CategoryAdmin(admin.ModelAdmin):
	prepopulated_fields = {
		'slug': ('name',)
	}
admin.site.register(Category, CategoryAdmin)

class TopicAdmin(admin.ModelAdmin):
	list_display = ('question', 'category')
	list_filter = ('category',)
admin.site.register(Topic, TopicAdmin)