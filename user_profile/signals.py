from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Profile, Teacher


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

    if hasattr(instance.profile, 'teacher'):
        instance.profile.teacher.save()

    elif instance.groups.filter(name='Teachers').exists():
        # if the entry in the teacher table doesn't exist but the user has group teacher, create the entry

        t = Teacher()
        t.teacher = instance.profile
        t.save()
