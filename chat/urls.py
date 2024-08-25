from django.urls import path
from .views import *

app_name = 'chat'
urlpatterns = [
    path('start-chat/<int:dest_pk>/', start_chat, name='chat-start'),
    path('view/', chat_home, name='chat-home'),
    path('view/<int:pk>/', chat_view, name='chat-view'),
    path('delete/<int:pk>/', chat_delete, name='chat-delete'),
]
