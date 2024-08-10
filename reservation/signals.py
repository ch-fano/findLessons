from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from reservation.models import Rating, Lesson, Availability


@receiver(post_save, sender=Rating)
def update_teacher_stars_on_save(sender, instance, **kwargs):
    teacher = instance.teacher
    ratings = Rating.objects.filter(teacher=teacher)

    if ratings.exists():
        average_stars = ratings.aggregate(Avg('stars'))['stars__avg']
        teacher.stars = average_stars
        teacher.save()


@receiver(post_delete, sender=Rating)
def update_teacher_stars_on_delete(sender, instance, **kwargs):
    teacher = instance.teacher
    ratings = Rating.objects.filter(teacher=teacher)

    if ratings.exists():
        average_stars = ratings.aggregate(Avg('stars'))['stars__avg']
        teacher.stars = average_stars
    else:
        teacher.stars = 0  # If there are no ratings, set to 0 or a default value

    teacher.save()


@receiver(post_save, sender=Lesson)
def delete_availability_on_lesson_create(sender, instance, **kwargs):
    # Delete existing availability with the same teacher and date
    Availability.objects.filter(
        teacher=instance.teacher,
        date__exact=instance.date
    ).delete()
