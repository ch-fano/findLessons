from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django import forms


class CreateUserForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label='User Type'
    )

    class Meta:
        model = User
        fields = ('user_type', 'username', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit)

        if self.cleaned_data['user_type'] == 'student':
            group = Group.objects.get(name="Students")
        else:
            group = Group.objects.get(name='Teachers')

        group.user_set.add(user)
        return user
