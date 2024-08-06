from datetime import timedelta, datetime, time
from django.utils import timezone
from django.utils.timezone import make_aware
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from braces.views import GroupRequiredMixin

from reservation.forms import AvailabilityForm, ReservationForm, LessonForm
from reservation.models import Availability, Lesson
from user_profile.models import Profile, Teacher


# Create your views here.

def get_reservation_home(request):
    ctx = {'title': 'Reservation', 'object_list': Teacher.objects.all()}

    return render(request, template_name='reservation/reservation_home.html', context=ctx)


def get_filtered_list(request, subject, city):

    context = {
        'subject': subject,
        'city': city,
        'title': 'Search teacher'
    }

    queryset = Teacher.objects.filter(subjects__icontains=subject, city__iexact=city)

    if request.method == 'POST':

        form = ReservationForm(request.POST)

        if form.is_valid():
            second_order = {'price': '-stars', '-stars': 'price'}
            start_date = timezone.make_aware(datetime.combine(form.cleaned_data['start_date'], time(0, 0)))
            end_date = timezone.make_aware(datetime.combine(form.cleaned_data['end_date'],
                                                            time(23, 59, 59)))
            order = form.cleaned_data['order']

            if order == 'stars':
                order = '-'+order

            queryset = queryset.filter(availability__date__range=[start_date, end_date]).order_by(
                                                                                order, second_order[order]).distinct()
    else:
        form = ReservationForm()

    context['teachers'] = queryset
    context['form'] = form

    return render(request, 'reservation/reservation_home.html', context)


def get_availability(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    is_me = (teacher.profile == request.user.profile) if request.user.is_authenticated else False

    today = make_aware(datetime.now())
    start_date = today - timedelta(days=today.weekday())  # Start of this week (Monday)
    end_date = start_date + timedelta(days=20)  # 3 weeks of days (3 weeks * 7 days - 1 day)

    # Filter availability for the calculated range
    filtered_availability = Availability.objects.filter(
        teacher=teacher,
        date__gte=start_date,
        date__lt=end_date
    ).order_by('date')

    # Create a dictionary to store events by date
    events_by_date = {}
    for availability in filtered_availability:
        date_str = availability.date.strftime('%Y-%m-%d')
        time_str = availability.date.strftime('%H:%M')
        if date_str not in events_by_date:
            events_by_date[date_str] = []
        events_by_date[date_str].append({
            'type': 'availability',
            'time': time_str,
            'id': availability.id
        })

    if is_me:
        # Filter lessons for the calculated range
        filtered_lessons = Lesson.objects.filter(
            teacher=teacher,
            date__gte=start_date,
            date__lt=end_date
        ).order_by('date')

        for lesson in filtered_lessons:
            date_str = lesson.date.strftime('%Y-%m-%d')
            time_str = lesson.date.strftime('%H:%M')
            if date_str not in events_by_date:
                events_by_date[date_str] = []
            events_by_date[date_str].append({
                'type': 'lesson',
                'time': time_str,
                'subject': lesson.subject,
                'id': lesson.id
            })

    # Sort events within each date
    for date_str in events_by_date:
        events_by_date[date_str].sort(key=lambda x: x['time'])

    # Create a list to store weeks and days for the calendar
    calendar_weeks = []
    current_date = start_date
    current_week = []

    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        current_week.append({
            'date': current_date,
            'events': events_by_date.get(date_str, [])
        })
        if len(current_week) == 7:
            calendar_weeks.append(current_week)
            current_week = []
        current_date += timedelta(days=1)

    if current_week:  # Add any remaining days in the last week
        calendar_weeks.append(current_week)

    ctx = {
        'title': 'Show availabilities',
        'teacher_name': teacher.profile.first_name + ' ' + teacher.profile.last_name,
        'today': today,
        'calendar_weeks': calendar_weeks,
        'is_me': is_me
    }

    return render(request, 'reservation/availability_list.html', context=ctx)


class AvailabilityCreateView(GroupRequiredMixin, CreateView):
    group_required = ['Teachers']
    model = Availability
    title = 'Set availability'
    template_name = 'reservation/entity_create_update.html'
    form_class = AvailabilityForm

    def get_success_url(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        teacher = get_object_or_404(Teacher, profile=profile)
        return reverse_lazy('availability-list', kwargs={'teacher_id': teacher.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        profile = get_object_or_404(Profile, user=self.request.user)
        teacher = get_object_or_404(Teacher, profile=profile)
        kwargs['teacher'] = teacher
        return kwargs

    def form_valid(self, form):
        profile = get_object_or_404(Profile, user=self.request.user)
        teacher = get_object_or_404(Teacher, profile=profile)
        form.instance.teacher = teacher
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['text'] = 'Set a new availability:'
        return ctx


class AvailabilityUpdateView(GroupRequiredMixin, UpdateView):
    group_required = ['Teachers']
    model = Availability
    title = 'Update availability'
    template_name = 'reservation/entity_create_update.html'
    form_class = AvailabilityForm

    def get_success_url(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        teacher = get_object_or_404(Teacher, profile=profile)
        return reverse_lazy('availability-list', kwargs={'teacher_id': teacher.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['text'] = 'Update the availability:'
        return ctx

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        profile = get_object_or_404(Profile, user=self.request.user)
        teacher = get_object_or_404(Teacher, profile=profile)
        kwargs['teacher'] = teacher
        return kwargs


class AvailabilityDeleteView(GroupRequiredMixin, DeleteView):
    group_required = ['Teachers']
    model = Availability
    title = 'Delete availability'
    template_name = 'reservation/availability_delete.html'

    def get_success_url(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        teacher = get_object_or_404(Teacher, profile=profile)
        return reverse_lazy('availability-list', kwargs={'teacher_id': teacher.pk})


class LessonDetailView(GroupRequiredMixin, DetailView):
    group_required = ['Teachers', 'Students']
    model = Lesson
    template_name = 'reservation/lesson_detail.html'


class LessonCreateView(GroupRequiredMixin, CreateView):
    group_required = ['Students']
    model = Lesson
    title = 'Book a lesson'
    template_name = 'reservation/entity_create_update.html'
    form_class = LessonForm

    def get_availability(self):
        return get_object_or_404(Availability, pk=self.kwargs['availability_id'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        availability = self.get_availability()
        kwargs['date'] = availability.date
        teacher_availabilities = Availability.objects.filter(teacher=availability.teacher)
        kwargs['teacher_availabilities'] = [a.date for a in teacher_availabilities]
        kwargs['teacher_subjects'] = availability.teacher.subjects.replace(',', '').split()
        return kwargs

    def form_valid(self, form):
        availability = self.get_availability()
        form.instance.student = self.request.user.profile
        form.instance.teacher = availability.teacher
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['text'] = 'Book a new lesson:'
        return ctx

    def get_success_url(self):
        availability = self.get_availability()
        return reverse_lazy('reservation:availability-list', kwargs={'teacher_id': availability.teacher.pk})