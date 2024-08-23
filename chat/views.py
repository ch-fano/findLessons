from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Chat
from user_profile.models import Profile

# Create your views here.

def get_chats_dicts(profile):
    chats = []
    for chat in profile.chats.all():
        chats.append(
            {'id': chat.pk,
            'other_participant': chat.get_other_participant(profile),
            'new_messages': chat.has_new_messages(profile)}
        )
    return chats

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
    current_chat = get_object_or_404(Chat, pk=pk)

    if request.user.profile not in current_chat.participants.all():
        return HttpResponseForbidden('You can only access to your chat')

    current_chat.read_messages(request.user.profile)

    ctx = {
        'receiver': current_chat.get_other_participant(request.user.profile),
        'messages': current_chat.messages.all(),
        'chat_name': current_chat.chat_name(),
        'chats': get_chats_dicts(request.user.profile)
    }
    return render(request, 'chat/chat.html', ctx)

@login_required
def chat_home(request):
    ctx = {
        'chats': get_chats_dicts(request.user.profile),
        'chat_name': 'None',
        'messages' : []
    }
    return render(request, 'chat/chat.html', ctx)
