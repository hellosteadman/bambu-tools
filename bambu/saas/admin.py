from django.contrib import admin
from django.utils.importlib import import_module
from django.conf import settings
from django import forms
from bambu.saas.models import *

class PlanFeatureInline(admin.TabularInline):
	model = PlanFeature
	extra = 0

class PriceInline(admin.TabularInline):
	model = Price
	extra = 0
	fields = ('currency', 'monthly', 'yearly')

class PlanAdmin(admin.ModelAdmin):
	list_display = ('name', 'price', 'plan_users')
	inlines = (PriceInline, PlanFeatureInline)
	
	def price(self, obj):
		prices = obj.prices.filter(currency = settings.CURRENCY_CODE)[:1]
		if prices.exists():
			return prices[0]
		
		return '(No price)'
	
	def plan_users(self, obj):
		return obj.users.count()
admin.site.register(Plan, PlanAdmin)

class FeatureAdminForm(forms.ModelForm):
	def clean_test_function(self):
		if not self.cleaned_data['is_boolean']:
			if not self.cleaned_data['test_function']:
				raise forms.ValidationError('This field is required for non-boolean features.')
			else:
				parts = self.cleaned_data['test_function'].split('.')
				mod = '.'.join(parts[:-1])
				func = parts[-1]
				
				try:
					mod = import_module(mod)
				except ImportError, ex:
					raise forms.ValidationError(unicode(ex))
				
				try:
					func = getattr(mod, func)
				except AttributeError, ex:
					raise forms.ValidationError(unicode(ex))
				
		return self.cleaned_data['test_function']

class FeatureAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'is_boolean')
	prepopulated_fields = {
		'slug': ('name',)
	}
	
	form = FeatureAdminForm
admin.site.register(Feature, FeatureAdmin)

class UserPlanChangeAdmin(admin.ModelAdmin):
	list_display = ('user', 'old_plan', 'new_plan')
admin.site.register(UserPlanChange, UserPlanChangeAdmin)

class UserPlanAdmin(admin.ModelAdmin):
	list_display = ('user', 'plan', 'period', 'started', 'expiry', 'paid')
	list_filter = ('plan', 'paid')
	date_hierarchy = 'started'
	readonly_fields = ('started', 'expiry', 'renewed')
admin.site.register(UserPlan, UserPlanAdmin)

class DiscountAdmin(admin.ModelAdmin):
	list_display = ('name', 'percent', 'months', 'code')
admin.site.register(Discount, DiscountAdmin)