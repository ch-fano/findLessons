from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from findLessons.forms import CreateUserForm
from reservation.forms import SearchForm
from user_profile.models import Profile


def homepage(request):
    ctx = {'title': 'findLessons'}

    if request.user.is_authenticated:
        ctx['profile'] = Profile.objects.get(user=request.user)

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            city = form.cleaned_data.get('city')
            return redirect('reservation:search', subject, city)
    else:
        form = SearchForm()

    ctx['form'] = form

    return render(request, template_name='homepage.html', context=ctx)


class UserCreateView(CreateView):
    form_class = CreateUserForm
    template_name = 'user_create.html'
    success_url = reverse_lazy('login')
