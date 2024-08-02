from datetime import datetime
from django.utils.timezone import make_aware
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from braces.views import GroupRequiredMixin

from reservation.forms import AvailabilityForm
from reservation.models import Availability
from user_profile.models import Profile, Teacher


# Create your views here.

def get_reservation_home(request):
    ctx = {'title': 'Reservation', 'object_list': Teacher.objects.all()}

    return render(request, template_name='reservation/reservation_home.html', context=ctx)


def get_filtered_list(request, subject, city):

    context = {
        'subject': subject,
        'city': city,
    }

    if request.method == 'POST':

        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        order_by = request.POST.get('order')

        queryset = Teacher.objects.filter(
            subjects__icontains=subject,
            city__iexact=city,
            date__range=[start_date, end_date]
        ).order_by(order_by)

        context['object_list'] = queryset
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['order_by'] = order_by
    else:

        queryset = Teacher.objects.filter(subjects__icontains=subject, city__iexact=city)
        context['object_list'] = queryset

    return render(request, 'reservation/reservation_home.html', context)


class SearchList(ListView):
    model = Teacher
    template_name = 'reservation/reservation_home.html'
    title = 'Reservation'

    def get_queryset(self):
        subject = self.request.resolver_match.kwargs['subject']
        city = self.request.resolver_match.kwargs['city']

        return Teacher.objects.filter(subjects__icontains=subject, city__iexact=city)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['subject'] = self.request.resolver_match.kwargs['subject']
        ctx['city'] = self.request.resolver_match.kwargs['city']

        return ctx


def get_availability(request, teacher_id):
    # check that the teacher id is correct
    teacher = get_object_or_404(Teacher, teacher_id=teacher_id)

    filtered_list = Availability.objects.filter(
        teacher_id=teacher_id,
        date__gt=make_aware(datetime.now())
    ).order_by('date')

    ctx = {'title': 'Show availabilities', 'list': filtered_list, 'is_me': (teacher.profile == request.user.profile)}

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
