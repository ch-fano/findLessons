from datetime import timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils import timezone
from tempus_dominus.widgets import DateTimePicker
from .models import Availability, Lesson, Rating


class ReservationForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    order = forms.ChoiceField(
        choices=[('price', 'Price'), ('stars', 'Stars')],
        initial='price',
        widget=forms.Select
    )


class LessonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.date = kwargs.pop('date', None)
        self.teacher_availabilities = kwargs.pop('teacher_availabilities', [])
        self.teacher_subjects = kwargs.pop('teacher_subjects', [])
        super(LessonForm, self).__init__(*args, **kwargs)

        self.fields['subject'] = forms.ChoiceField(
            choices=[(s, s) for s in self.teacher_subjects],
            widget=forms.Select,
            label="Select the subject",
            required=True
        )

        self.fields['date'] = forms.ChoiceField(
            choices=[(date, date.strftime('%Y-%m-%d %H:%M')) for date in self.teacher_availabilities],
            widget=forms.Select,
            label="Select availability date",
            required=True
        )

        if self.date:
            self.fields['date'].initial = [self.date]

        self.helper = FormHelper()
        self.helper.form_id = 'lesson_form'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Lesson
        fields = ['subject', 'date']


class AvailabilityForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super(AvailabilityForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'availability_form'
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
            availability_overlaps = Availability.objects.filter(
                teacher=self.teacher,
                date__gt=start_range,
                date__lt=end_range
            )
            lesson_overlaps = Lesson.objects.filter(
                teacher=self.teacher,
                date__gt=start_range,
                date__lt=end_range
            )
            if current_instance_id:
                availability_overlaps = availability_overlaps.exclude(id=current_instance_id)

            if availability_overlaps.exists() or lesson_overlaps.exists():
                raise forms.ValidationError(
                    "This teacher already has an event within 1 hour of the selected date and time.")

        return cleaned_data


class SearchForm(forms.Form):
    subject = forms.CharField(label='Subject', max_length=100, required=True)
    city = forms.CharField(label='City', max_length=100, required=True)


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars']
        widgets = {
            'stars': forms.RadioSelect(choices=[(i, f"{i} ★") for i in range(0, 6)]),
        }
