from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from user_profile.forms import ProfileForm
from user_profile.models import Profile, Teacher


# Create your views here.


@login_required
def profile_home(request):
    ctx = {'title': 'User profile', 'profile': Profile.objects.get(user=request.user)}

    if request.user.groups.filter(name='Teachers').exists():
        ctx['teachers'] = Teacher.objects.filter(teacher=ctx['profile'])
    else:
        ctx['teachers'] = None

    return render(request, template_name='user_profile/profile.html', context=ctx)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    title = 'Update Profile'
    form_class = ProfileForm
    template_name = 'user_profile/profile_update.html'
    success_url = reverse_lazy('user_profile:profile')

    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)

