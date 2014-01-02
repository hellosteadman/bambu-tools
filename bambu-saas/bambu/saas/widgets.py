from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.html import escape, conditional_escape

class ImageRadioInput(forms.widgets.RadioInput):
	def __init__(self, name, value, attrs, choice, index):
		super(ImageRadioInput, self).__init__(name, value, attrs, choice, index)
		self.choice_label = force_unicode(choice[2])
		self.choice_image = force_unicode(choice[1])
	
	def __unicode__(self):
		if 'id' in self.attrs:
			label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
		else:
			label_for = ''
		
		choice_label = conditional_escape(force_unicode(self.choice_label))
		choice_image = '<img src="%s" alt="%s" />' % (
			conditional_escape(force_unicode(self.choice_image)),
			choice_label
		)
		
		return mark_safe(u'<label%s>%s %s %s</label>' % (
			label_for, self.tag(), choice_image, choice_label)
		)

class ImageRadioFieldRenderer(forms.widgets.RadioFieldRenderer):
	def __iter__(self):
		for i, choice in enumerate(self.choices):
			yield ImageRadioInput(
				self.name, self.value, self.attrs.copy(), choice, i
			)
	
	def __getitem__(self, idx):
		choice = self.choices[idx]
		
		return ImageRadioInput(
			self.name, self.value, self.attrs.copy(), choice, idx
		)

class ImageRadioSelect(forms.widgets.RadioSelect):
	renderer = ImageRadioFieldRenderer