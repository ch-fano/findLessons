from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from user_profile.models import Profile, Teacher


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'profile_form'
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', 'Submit'))

        if self.instance:
            self.fields['picture'].widget.attrs['value'] = self.instance.picture.url
            self.fields['first_name'].widget.attrs['value'] = self.instance.first_name
            self.fields['last_name'].widget.attrs['value'] = self.instance.last_name
            self.fields['email'].widget.attrs['value'] = self.instance.email
            self.fields['tel_number'].widget.attrs['value'] = self.instance.tel_number

    class Meta:
        model = Profile
        fields = ['picture', 'first_name', 'last_name', 'email', 'tel_number']


class TeacherForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'teacher_form'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

        if self.instance:
            self.fields['city'].widget.attrs['value'] = self.instance.city
            self.fields['subjects'].widget.attrs['value'] = self.instance.subjects
            self.fields['price'].widget.attrs['value'] = self.instance.price

    class Meta:
        model = Teacher
        fields = ['city', 'subjects', 'price']
