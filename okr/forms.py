from django.forms import ModelForm
from okr.models import Objective, KeyResult


# Configured to Bootstrap classes
class KeyResultForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(KeyResultForm, self).__init__(*args, **kwargs)
		for field_name, field in self.fields.items():
			field.widget.attrs['class'] = 'form-control input-sm'

	class Meta:
		model = KeyResult
		fields = ('name', 'type_data', 'expected', 'obtained')
