from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
	def save(self, commit = True):
		user = User.objects.create_user(
			username = self.cleaned_data['username'],
			password = self.cleaned_data['password'],
			email = self.cleaned_data.get('email')
		)
		
		user.first_name = self.cleaned_data.get('first_name', '')
		user.last_name = self.cleaned_data.get('last_name', '')
		user.save()
		
		return user
	
	class Meta:
		model = User
		fields = ('username', 'password', 'first_name', 'last_name', 'email')