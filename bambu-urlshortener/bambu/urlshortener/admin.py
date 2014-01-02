from django.contrib import admin
from bambu.urlshortener.models import ShortURL

class ShortURLAdmin(admin.ModelAdmin):
	list_display = ('url', 'slug', 'visits', 'last_visited')
	readonly_fields = ('slug', 'visits', 'last_visited')

admin.site.register(ShortURL, ShortURLAdmin)