from datetime import timedelta, datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils import timezone
from tempus_dominus.widgets import DateTimePicker, DatePicker
from .models import Availability


class ReservationForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    order = forms.ChoiceField(
        choices=[('price', 'Price'), ('stars', 'Stars')],
        initial='price',
        widget=forms.Select
    )


class AvailabilityForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
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

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        current_instance_id = self.instance.id if self.instance else None

        if date and date < timezone.now():
            raise forms.ValidationError("The selected date cannot be in the past.")

        if self.teacher and date:
            start_range = date - timedelta(hours=1)
            end_range = date + timedelta(hours=1)
            overlaps = Availability.objects.filter(
                teacher=self.teacher,
                date__gt=start_range,
                date__lt=end_range
            )
            if current_instance_id:
                overlaps = overlaps.exclude(id=current_instance_id)

            if overlaps.exists():
                raise forms.ValidationError(
                    "This teacher already has an availability within 1 hour of the selected date and time.")

        return cleaned_data


class SearchForm(forms.Form):
    subject = forms.CharField(label='Subject', max_length=100, required=True)
    city = forms.CharField(label='City', max_length=100, required=True)
