"""
URL configuration for findLessons project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from .views import *

app_name = 'reservation'

urlpatterns = [
    path('', get_reservation_home, name='reservation_home'),
    path('search/<str:subject>/<str:city>/', get_filtered_list, name='search'),
    path('availability/<int:teacher_id>/', get_calendar, name='availability-list'),
    path('availability/create/', AvailabilityCreateView.as_view(), name='availability-create'),
    path('availability/update/<int:pk>/', AvailabilityUpdateView.as_view(), name='availability-update'),
    path('availability/delete/<int:pk>/', AvailabilityDeleteView.as_view(), name='availability-delete'),
    path('lesson/<int:pk>/', LessonDetailView.as_view(), name='lesson-view'),
    path('lesson/create/<int:availability_id>/', LessonCreateView.as_view(), name='lesson-create'),
    path('lesson/delete/<int:pk>/<str:action>/', delete_lesson, name='lesson-delete'),
]
