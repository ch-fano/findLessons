from datetime import datetime
from django.utils.timezone import make_aware
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from braces.views import GroupRequiredMixin

from reservation.forms import AvailabilityForm
from reservation.models import Availability
from user_profile.models import Profile, Teacher


# Create your views here.


def reservation_home(request):
    return render(request, 'reservation/home.html')


def get_availability(request, teacher):
    # check that the teacher id is correct
    get_object_or_404(Teacher, teacher_id=teacher)

    filtered_list = Availability.objects.filter(
        teacher_id=teacher,
        available=True,
        date__gt=make_aware(datetime.now())
    ).order_by('date')

    ctx = {'title': 'Show availabilities', 'list': filtered_list}
    return render(request, template_name='reservation/availability_list.html', context=ctx)


class CreateAvailabilityView(GroupRequiredMixin, CreateView):
    group_required = ["Teachers"]
    model = Availability
    title = 'Set availability'
    template_name = 'reservation/availability_create.html'
    success_url = reverse_lazy('user_profile:profile')
    form_class = AvailabilityForm

    def form_valid(self, form):
        profile = get_object_or_404(Profile, user=self.request.user)
        form.instance.teacher = profile
        return super().form_valid(form)
