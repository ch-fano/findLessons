from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from user_profile.models import Profile


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'profile_form'
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Profile
        fields = ['picture', 'first_name', 'last_name', 'email', 'tel_number']