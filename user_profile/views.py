from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin

from user_profile.forms import ProfileForm
from user_profile.models import Profile, Teacher


# Create your views here.


@login_required
def profile_home(request):
    profile = get_object_or_404(Profile, user=request.user)
    ctx = {'title': 'User profile', 'profile': profile}

    if request.user.is_superuser:
        template = 'user_profile/admin_profile.html'

    elif request.user.groups.filter(name='Teachers').exists():
        template = 'user_profile/teacher_profile.html'
        teacher = get_object_or_404(Teacher, teacher=profile)
        ctx['teacher'] = teacher

    else:
        template = 'user_profile/student_profile.html'

    return render(request, template_name=template, context=ctx)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    title = 'Update Profile'
    form_class = ProfileForm
    template_name = 'user_profile/profile_update.html'
    success_url = reverse_lazy('user_profile:profile')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)


class TeacherUpdateView(GroupRequiredMixin, UpdateView):
    group_required = ["Teachers"]
    model = Teacher
    title = 'Update Teacher'
    # form_class = TeacherForm
    template_name = 'user_profile/teacher_update.html'
    success_url = reverse_lazy('user_profile:profile')
    fields = ['city', 'subjects', 'price']

    def get_object(self, queryset=None):
        profile = get_object_or_404(Profile, user=self.request.user)
        return get_object_or_404(Teacher, teacher=profile)

