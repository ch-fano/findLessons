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

            return redirect(reverse_lazy('user_profile:make-request'))

        else:
            user = form.save(commit=True)
            form.save_m2m()  # Save many-to-many relationships, like adding the user to a group

            return redirect(reverse_lazy('login'))
