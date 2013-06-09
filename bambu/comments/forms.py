from django import forms
from bambu.comments.models import Comment

class CommentForm(forms.ModelForm):
	h0n3ytr4p = forms.CharField(
		label = u'What is 1 + 1?', required = False,
		help_text = u'Do not enter any text into this field. This is a honeytrap for spam bots.'
	)
	
	def __init__(self, *args, **kwargs):
		super(CommentForm, self).__init__(*args, **kwargs)
		self.fields['name'].label = u'Your name'
		self.fields['email'].label = u'Email address'
		self.fields['email'].help_text = u'It won\'t be shared'
		self.fields['body'].label = u'Your comment'
	
	class Meta:
		model = Comment
		fields = ('name', 'email', 'website', 'body')