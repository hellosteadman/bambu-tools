from django.contrib import admin
from bambu.enquiries.models import Enquiry

class EnquiryAdmin(admin.ModelAdmin):
	list_display = ('subject', 'name', 'sent')
	date_hierarchy = 'sent'
	readonly_fields = ('name', 'email', 'subject', 'message', 'sent')
	
	def has_add_permission(self, request):
		return False

admin.site.register(Enquiry, EnquiryAdmin)