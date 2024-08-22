from django.db import models
from user_profile.models import Profile

# Create your models here.


class Chat(models.Model):
    participants = models.ManyToManyField(Profile, related_name='chats')

    def chat_name(self):
        return f"chat_{self.pk}"

    def __str__(self):
        return 'Chat between ' + ','.join([profile.user.username for profile in self.participants.all()])

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(Profile, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)

    def __str__(self):
        return f"{self.sender.user.username}: {self.content[:20]}"
