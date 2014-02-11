from django import forms
from django.forms import ModelForm, ValidationError
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from okr.models import Objective, KeyResult
import datetime


class ObjectiveForm(ModelForm):

	class Meta:
		model = Objective
		fields = ('name', 'end_date')

	# Configured to Bootstrap classes
	def __init__(self, *args, **kwargs):
		super(ObjectiveForm, self).__init__(*args, **kwargs)
		for field_name, field in self.fields.items():
			field.widget.attrs['class'] = 'form-control input-sm'

	def clean(self):
		end_date = self.cleaned_data.get('end_date', None)

		# end_date >= pub_date
		if end_date and (end_date < datetime.date.today()):
			self._errors['end_date'] = 'End date must be later than today.'

		return self.cleaned_data



class KeyResultForm(ModelForm):

	class Meta:
		model = KeyResult
		fields = ('name', 'type_data', 'expected', 'obtained')

	# Configured to Bootstrap classes
	def __init__(self, *args, **kwargs):
		super(KeyResultForm, self).__init__(*args, **kwargs)
		for field_name, field in self.fields.items():
			field.widget.attrs['class'] = 'form-control input-sm'

	def clean(self):
		obtained = self.cleaned_data.get('obtained', None)
		expected = self.cleaned_data.get('expected', None)
		type_data = self.cleaned_data.get('type_data', None)

		# obtained <= expected
		if ( obtained > expected ):
			self._errors['obtained'] = 'Obtained can not be greater than expected.'
			# raise ValidationError('Obtained can not be greater than expected.')

		# if it's binary: obtained = 0 or 1 and expected = 1
		if ( type_data == KeyResult.BINARY ):
			if not (obtained == 0 or obtained == 1):
				self._errors['obtained'] = 'Obtained must be 0 or 1.'
				# raise ValidationError('Obtained must be 0 or 1.')

			if not (expected == 1):
				self._errors['expected'] = 'Expected must be 1.'
				# raise ValidationError('Expected must be 1.')

		return self.cleaned_data


class AuthForm(AuthenticationForm):
	
	# Configured to Bootstrap classes
	def __init__(self, *args, **kwargs):
		super(AuthForm, self).__init__(*args, **kwargs)
		for field_name, field in self.fields.items():
			field.widget.attrs['class'] = 'form-control input-sm'

	def clean(self):
		username = self.cleaned_data.get('username', None)
		password = self.cleaned_data.get('password', None)
		user = authenticate(username=username, password=password)
		if not user:
			raise ValidationError("Sorry, that login was invalid. Please try again.")
		else:
			if not user.is_active:
				raise ValidationError("Sorry, that user is inactive.")

		return self.cleaned_data

	def login(self, request):
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		return user


class RegisterForm(UserCreationForm):
	email = forms.EmailField(required=True)

	# Configured to Bootstrap classes
	def __init__(self, *args, **kwargs):
		super(RegisterForm, self).__init__(*args, **kwargs)
		for field_name, field in self.fields.items():
			field.widget.attrs['class'] = 'form-control input-sm'

	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2')

	def save(self, commit=True):
		user = super(RegisterForm, self).save(commit=False)
		user.email = self.cleaned_data["email"]
		if commit:
			user.save()
		return user


class ChangePasswordForm(PasswordChangeForm):

	# Configured to Bootstrap classes
	def __init__(self, user, *args, **kwargs):
		super(ChangePasswordForm, self).__init__(user, *args, **kwargs)
		for field_name, field in self.fields.items():
			field.widget.attrs['class'] = 'form-control input-sm'
