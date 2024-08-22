from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Chat
from user_profile.models import Profile

# Create your views here.

@login_required
def start_chat(request, dest_pk):
    sender = request.user.profile
    receiver = get_object_or_404(Profile, pk=dest_pk)

    if sender == receiver:
        return HttpResponseBadRequest('You cannot chat with yourself' )

    chat = Chat.objects.filter(participants=sender).filter(participants=receiver).distinct().first()

    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(sender, receiver)
        chat.save()

    return redirect('chat:chat-view', pk=chat.pk)

@login_required
def chat_view(request, pk):
    chat = get_object_or_404(Chat, pk=pk)

    if request.user.profile not in chat.participants.all():
        return HttpResponseForbidden('You can only access to your chat')

    messages = chat.messages.all()

    return render(request, 'chat/chat.html', {'chat': chat,
                                              'chat_name': chat.chat_name(),
                                              'messages': messages})
