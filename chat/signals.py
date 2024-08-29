from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Chat, Visibility

@receiver(m2m_changed, sender=Chat.participants.through)
def create_visibility_instance(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set:
            profile = model.objects.get(pk=pk)

            # Check if the Visibility already exists to avoid duplicates
            Visibility.objects.get_or_create(chat=instance, participant=profile)
