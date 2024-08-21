from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Chat
from django.contrib.auth.models import User

# Create your views here.

@login_required
def start_chat(request, dest_pk):
    user1 = request.user
    user2 = get_object_or_404(User, pk=dest_pk)

    if user1 == user2:
        return HttpResponseBadRequest('You cannot chat with yourself' )

    chat, created = Chat.objects.get_or_create(participants__in=[user1, user2])

    return redirect('chat:chat-view', pk=chat.pk)

@login_required
def chat_view(request, pk):
    chat = get_object_or_404(Chat, pk=pk)

    #if request.user not in chat.participants.all():
        #return HttpResponseForbidden('You can only access to your chat')

    return render(request, 'chat/chat.html', {'chat': chat})
