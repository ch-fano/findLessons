from django import forms
from tempus_dominus.widgets import DateTimePicker
from .models import Availability


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['date']
        widgets = {
            'date': DateTimePicker(
                options={
                    'useCurrent': True,
                    'collapse': False,
                    'sideBySide': True,
                    'format': 'YYYY-MM-DD HH:mm',
                },
                attrs={
                    'input_toggle': True,
                    'input_group': True,
                }
            ),
        }


class SearchForm(forms.Form):
    subject = forms.CharField(label='Subject', max_length=100, required=True)
    city = forms.CharField(label='City', max_length=100, required=True)
