from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from user_profile.models import Profile

# Create your models here.


class Chat(models.Model):
    participants = models.ManyToManyField(Profile, related_name='chats')

    def chat_name(self):
        return f'chat_{self.pk}'

    def get_other_participant(self, profile):
        try:
            other_participant = self.participants.exclude(pk=profile.pk).first()
            if other_participant:
                return other_participant
            else:
                return 'Unknown'
        except ObjectDoesNotExist:
            return 'Unknown'

    def has_new_messages(self, profile, ):
        sender = self.get_other_participant(profile)
        return self.messages.filter(sender=sender, read=False).exists()

    def read_messages(self, profile):
        sender = self.get_other_participant(profile)
        for msg in self.messages.filter(sender=sender, read=False):
            msg.read = True
            msg.save()

    def __str__(self):
        return 'Chat between ' + ','.join([profile.user.username for profile in self.participants.all()])

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(Profile, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ('timestamp',)

    def __str__(self):
        return f"{self.sender.user.username}: {self.content[:20]}"

class Visibility(models.Model):
    chat = models.ForeignKey(Chat, related_name='visibility', on_delete=models.CASCADE)
    participant = models.ForeignKey(Profile, related_name='visibility', on_delete=models.CASCADE)
    visible = models.BooleanField(default=True)