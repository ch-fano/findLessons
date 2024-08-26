from django.http import Http404, HttpResponseForbidden, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.models import Group
from django.views.generic import UpdateView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from braces.views import GroupRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail

from reservation.models import Lesson, Rating
from .models import *
from .forms import ProfileForm, TeacherForm, RequestForm

# Create your views here.view

@login_required
def profile_home(request):
    profile = get_object_or_404(Profile, user=request.user)
    ctx = {'title': 'User profile', 'profile': profile, 'is_me': True, 'is_student': False, 'is_admin':False}

    notifications = request.user.profile.notifications.all()
    if notifications.exists():
        news = True
        for n in notifications:
            news = news and n.read
        ctx['news'] = not news
    else:
        ctx['news'] = False

    chat_news = False
    for chat in profile.chats.all():
        chat_news = chat_news or chat.has_new_messages(profile)
    ctx['chat_news'] = chat_news

    if request.user.is_superuser:
        template = 'user_profile/admin_profile.html'
        ctx['requests'] = Request.objects.all()
        ctx['is_admin'] = True
    elif request.user.groups.filter(name='Teachers').exists():
        template = 'user_profile/teacher_profile.html'
        teacher = get_object_or_404(Teacher, profile=profile)
        ctx['teacher'] = teacher
    else:
        template = 'user_profile/student_profile.html'
        ctx['today'] = timezone.now()
        ctx['lessons'] = Lesson.objects.all().filter(student=profile).order_by('date')
        ctx['ratings'] = Rating.objects.filter(student=profile)
        ctx['is_student'] = True

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
    use_history = True if request.GET.get('source', None) else False
    ctx = {'title': 'View profile', 'profile': profile, 'is_me': False, 'is_admin': False, 'use_history': use_history}

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
    template_name = 'user_profile/profile_teacher_request_update.html'
    success_url = reverse_lazy('user_profile:profile')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)


class TeacherUpdateView(GroupRequiredMixin, UpdateView):
    group_required = ['Teachers']
    model = Teacher
    title = 'Update Teacher'
    form_class = TeacherForm
    template_name = 'user_profile/profile_teacher_request_update.html'
    success_url = reverse_lazy('user_profile:profile')

    def get_object(self, queryset=None):
        profile = get_object_or_404(Profile, user=self.request.user)
        return get_object_or_404(Teacher, profile=profile)


def get_notifications(request):
    notifications = request.user.profile.notifications.all()
    for n in notifications:
        n.read = True
        n.save()

    ctx = {'title': 'View notifications', 'news': notifications}

    return render(request, template_name='user_profile/news_list.html', context=ctx)


@login_required
def delete_notification(request, pk):
    Notification.objects.get(pk=pk).delete()
    return redirect('user_profile:view-notification')


class RequestCreateView(CreateView):
    model = Request
    form_class = RequestForm
    title = 'Registration request'
    template_name = 'user_profile/profile_teacher_request_update.html'
    success_url = reverse_lazy('homepage')

    def get(self, request, *args, **kwargs):
        if 'teacher_username' not in request.session or 'teacher_password' not in request.session:
            return redirect('login')

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        username = self.request.session.get('teacher_username')
        password = self.request.session.get('teacher_password')

        if not username or not password:
            return redirect('login')

        request_instance = form.save(commit=False)
        request_instance.username = username
        request_instance.set_password(password)
        request_instance.save()

        self.request.session.pop('teacher_username', None)
        self.request.session.pop('teacher_password', None)

        return super().form_valid(form)


class RequestDetailView(UserPassesTestMixin, DetailView):
    model = Request
    title = 'View request'
    template_name = 'user_profile/request_detail.html'

    def test_func(self):
        return self.request.user.is_superuser

@login_required
def delete_request(request, pk, action):

    if not request.user.is_superuser:
        return HttpResponseForbidden("Superuser permission needed")
    if action not in ['accept', 'reject']:
        return HttpResponseBadRequest("Invalid action parameter")

    teacher_request = get_object_or_404(Request, pk=pk)

    subject = 'FindLessons: outcome of the registration request'
    message = (f'Hello {teacher_request.first_name}, \nwe are sorry but your registration request was rejected.'
               f'\n\nBest regards, \nFindLessons team.')
    from_email = 'findlessons2024@gmail.com'
    recipient_list = [teacher_request.email]

    if action == 'accept':
        user = User(username=teacher_request.username)
        user.set_password(teacher_request.get_password())
        user.save()

        teachers_group = Group.objects.get(name='Teachers')
        user.groups.add(teachers_group)

        user.profile.first_name = teacher_request.first_name
        user.profile.last_name = teacher_request.last_name
        user.profile.email = teacher_request.email
        user.profile.save()

        message = (f'Hello {teacher_request.first_name}, \nWe are pleased to announce that your registration request '
               f'has been accepted.\nYou can now log in to your account with the following username: '
                   f'{teacher_request.username}\n\nBest regards, \nFindLessons team.')

    # Delete the ID for privacy reasons
    if teacher_request.identification:
        teacher_request.identification.delete(save=False)

    teacher_request.delete()

    send_mail(subject, message, from_email, recipient_list)

    return redirect('user_profile:profile')
