from django.template import Library
from django.forms.widgets import CheckboxInput, ClearableFileInput
from django.forms import DateTimeField, DateField, FileField

register = Library()

@register.filter()
def is_checkbox(field):
	return isinstance(field.field.widget, CheckboxInput)

@register.filter()
def is_datefield(field):
	return isinstance(field.field, (DateTimeField, DateField))

@register.filter()
def is_clearable_filefield(field):
	return isinstance(field.field.widget, ClearableFileInput)