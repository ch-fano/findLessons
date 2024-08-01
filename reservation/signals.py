from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg
from reservation.models import Rating


@receiver(post_save, sender=Rating)
def update_teacher_stars(sender, instance, **kwargs):
    teacher_profile = instance.teacher
    ratings = Rating.objects.filter(teacher=teacher_profile)

    if ratings.exists():
        average_stars = ratings.aggregate(Avg('stars'))['stars__avg']
        teacher_profile.teacher.stars = average_stars
        teacher_profile.teacher.save()
