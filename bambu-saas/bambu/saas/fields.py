from django.forms.fields import ChoiceField
from bambu.saas.widgets import ImageRadioSelect

class ImageChoiceField(ChoiceField):
	widget = ImageRadioSelect
	
	def valid_value(self, value):
		for choice in self.choices:
			if choice[0] == value:
				return True
		
		return False