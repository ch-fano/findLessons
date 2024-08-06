from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Profile, Teacher
from .forms import ProfileForm, TeacherForm

# Create your views here.view


@login_required
def profile_home(request):
    profile = get_object_or_404(Profile, user=request.user)
    ctx = {'title': 'User profile', 'profile': profile, 'is_me':True}

    if request.user.is_superuser:
        template = 'user_profile/admin_profile.html'
    elif request.user.groups.filter(name='Teachers').exists():
        template = 'user_profile/teacher_profile.html'
        teacher = get_object_or_404(Teacher, profile=profile)
        ctx['teacher'] = teacher
    else:
        template = 'user_profile/student_profile.html'

    if request.method == 'POST':
        profile_data = {key: request.POST[key] for key in ('first_name', 'last_name', 'email', 'tel_number', 'picture')
                        if key in request.POST}
        profile_form = ProfileForm(profile_data, request.FILES, instance=profile)

        teacher_form = None
        if 'teacher' in ctx:
            teacher_data = {key: request.POST[key] for key in ('city', 'subjects', 'price') if key in request.POST}
            teacher_form = TeacherForm(teacher_data, instance=ctx['teacher'])

        if profile_form.is_valid() and (teacher_form is None or teacher_form.is_valid()):
            profile_form.save()
            profile.refresh_from_db()
            ctx['profile'] = profile

            if teacher_form:
                teacher_form.save()
                ctx['teacher'].refresh_from_db()

    return render(request, template_name=template, context=ctx)


def view_profile(request, pk):

    profile = get_object_or_404(Profile, pk=pk)
    ctx = {'title': 'View profile', 'profile': profile, 'is_me': False}

    if profile.user.is_superuser:
        raise Http404
    elif profile.user.groups.filter(name='Teachers').exists():
        template = 'user_profile/teacher_profile.html'
        teacher = get_object_or_404(Teacher, profile=profile)
        ctx['teacher'] = teacher
    else:
        template = 'user_profile/student_profile.html'

    return render(request, template_name=template, context=ctx)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    title = 'Update Profile'
    form_class = ProfileForm
    template_name = 'user_profile/profile_update.html'

    def get_success_url(self):
        if self.request.user.groups.filter(name='Teachers').exists():

            # if not edited go to the teacher form
            if len(self.request.user.profile.teacher.city) == 0:
                return reverse_lazy('user_profile:set-teacher')

        return reverse_lazy('user_profile:profile')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)


class TeacherUpdateView(GroupRequiredMixin, UpdateView):
    group_required = ['Teachers']
    model = Teacher
    title = 'Update Teacher'
    form_class = TeacherForm
    template_name = 'user_profile/profile_update.html'
    success_url = reverse_lazy('user_profile:profile')

    def get_object(self, queryset=None):
        profile = get_object_or_404(Profile, user=self.request.user)
        return get_object_or_404(Teacher, profile=profile)

