from django.template import Library
from django.forms.widgets import CheckboxInput, ClearableFileInput, CheckboxSelectMultiple
from django.forms import DateTimeField, DateField, FileField, TextInput, EmailField
from django.utils.safestring import mark_safe

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

@register.filter()
def bootstrapped(field):
	if isinstance(field.field.widget, CheckboxSelectMultiple):
		return mark_safe('<div class="checkbox">%s</div>' % field)
	
	classes = field.field.widget.attrs.get('class', '').split(' ')
	if isinstance(field.field.widget, TextInput):
		if field.field.required:
			field.field.widget.attrs['required'] = 'required'
	
	classes.append('form-control')
	field.field.widget.attrs['class'] = ' '.join(set(classes)).strip()
	return unicode(field)