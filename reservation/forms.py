from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from tempus_dominus.widgets import DateTimePicker, DatePicker
from .models import Availability


class AvailabilityForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AvailabilityForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'profile_form'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

        if self.instance:
            self.fields['date'].widget.attrs['value'] = self.instance.date

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
