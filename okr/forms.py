from django.forms import ModelForm, ValidationError
from okr.models import Objective, KeyResult


# Configured to Bootstrap classes
class KeyResultForm(ModelForm):

	class Meta:
		model = KeyResult
		fields = ('name', 'type_data', 'expected', 'obtained')


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
