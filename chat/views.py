from django.dispatch import receiver
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Chat, Visibility
from user_profile.models import Profile

# Create your views here.

def get_chats_dicts(profile):
    chats = []
    for chat in profile.chats.all():
        new_msg = chat.has_new_messages(profile)

        if chat.visibility.get(participant=profile).visible or new_msg:
            other_participant = chat.get_other_participant(profile)
            if other_participant:
                chats.append(
                    {'id': chat.pk,
                    'other_participant': other_participant,
                    'new_messages': new_msg,}
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
    else:
        chat_visibility  = sender.visibility.filter(chat=chat).first()
        chat_visibility.visible = True
        chat_visibility.save()

    return redirect('chat:chat-view', pk=chat.pk)

@login_required
def chat_view(request, pk):
    current_chat = get_object_or_404(Chat, pk=pk)
    chat_receiver = current_chat.get_other_participant(request.user.profile)

    if request.user.profile not in current_chat.participants.all():
        return HttpResponseForbidden('You can only access to your chat')

    # Prevent accessing "deleted" chat via url and chats without a receiver
    if not current_chat.visibility.get(participant=request.user.profile).visible or chat_receiver is None:
        return redirect('chat:chat-home')

    current_chat.read_messages(request.user.profile)

    ctx = {
        'receiver': chat_receiver,
        'messages': current_chat.messages.all(),
        'chat_name': current_chat.chat_name(),
        'chats': get_chats_dicts(request.user.profile),
        'current_chat_id': current_chat.pk,
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

@login_required
def chat_delete(request, pk):
    chat = get_object_or_404(Chat, pk=pk)

    if request.user.profile not in chat.participants.all():
        return HttpResponseForbidden('You can only delete your chat')

    delete = True
    for v in chat.visibility.all():
        if v.participant == request.user.profile:
            v.visible = False
            v.save()

        delete = delete and not v.visible

    # Delete the chat only if it is not visible for all of its participants
    if delete:
        chat.delete()

    return redirect('chat:chat-home')