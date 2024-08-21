from django.urls import path
from .views import *

app_name = 'chat'
urlpatterns = [
    path('start-chat/<int:dest_pk>/', start_chat, name='chat-start'),
    path('chat/<int:pk>/', chat_view, name='chat-view'),
]
