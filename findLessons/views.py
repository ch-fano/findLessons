from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from findLessons.forms import CreateUserForm


def homepage(request):
    ctx = {'title': 'findLessons'}
    return render(request, template_name='homepage.html', context=ctx)


class UserCreateView(CreateView):
    form_class = CreateUserForm
    template_name = 'user_create.html'
    success_url = reverse_lazy('login')
