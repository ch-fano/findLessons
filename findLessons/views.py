from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from findLessons.forms import CreateUserForm
from reservation.forms import SearchForm
from user_profile.models import Profile


def homepage(request):

    ctx = {'title': 'FindLessons'}

    if request.user.is_authenticated:
        ctx['profile'] = Profile.objects.get(user=request.user)

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            city = form.cleaned_data.get('city')
            return redirect('reservation:search', subject.lower(), city.lower())
    else:
        form = SearchForm()

    ctx['form'] = form

    return render(request, template_name='homepage.html', context=ctx)


class UserCreateView(CreateView):
    form_class = CreateUserForm
    template_name = 'user_create.html'

    def form_valid(self, form):
        user_type = form.cleaned_data.get('user_type')

        if user_type == 'teacher':
            self.request.session['teacher_username'] = form.cleaned_data.get('username')
            self.request.session['teacher_password'] = form.cleaned_data.get('password1')

            return redirect(reverse_lazy('user_profile:request-create'))

        else:
            user = form.save(commit=True)
            form.save_m2m()  # Save many-to-many relationships, like adding the user to a group

            return redirect(reverse_lazy('login'))

class CustomPasswordChangeView(LoginRequiredMixin,PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('user_profile:profile')

    def form_valid(self, form):
        messages.success(self.request, "Your password was changed successfully.")
        return super().form_valid(form)
