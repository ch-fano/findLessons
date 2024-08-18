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

app_name = 'user_profile'
urlpatterns = [
    path('', profile_home, name='profile'),
    path('view/<int:pk>/', view_profile, name='view-profile'),
    path('set/', ProfileUpdateView.as_view(), name='set-profile'),
    path('set/teacher/', TeacherUpdateView.as_view(), name='set-teacher'),
    path('notification/', get_notifications, name='view-notification'),
    path('notification/delete/<int:pk>/', delete_notification, name='delete-notification'),
    path('request/', RequestCreateView.as_view(), name='make-request'),
]

