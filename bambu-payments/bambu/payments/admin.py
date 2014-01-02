from django.contrib import admin
from bambu.payments.models import TaxRate, Payment, Status

class TaxRateAdmin(admin.ModelAdmin):
	list_display = ('name', 'shorthand', 'payable_percent')
admin.site.register(TaxRate, TaxRateAdmin)

class StatusInline(admin.StackedInline):
	model = Status
	readonly_fields = ('changed', 'state')
	extra = 0

class PaymentAdmin(admin.ModelAdmin):
	list_display = ('id', 'content_object', 'customer', 'created', 'net_amount', 'tax_amount')
	date_hierarchy = 'created'
	readonly_fields = (
		'customer', 'recurring', 'trial_months', 'currency',
		'net_amount', 'postage', 'tax_amount', 'tax_rate', 'remote_id'
	)
	
	inlines = [StatusInline]
admin.site.register(Payment, PaymentAdmin)