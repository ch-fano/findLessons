from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from findLessons.forms import CreateUserForm
from user_profile.models import Profile


def homepage(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)

    return render(request, template_name='homepage.html', context={'title': 'findLessons', 'profile': profile})


class UserCreateView(CreateView):
    form_class = CreateUserForm
    template_name = 'user_create.html'
    success_url = reverse_lazy('login')
