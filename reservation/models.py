from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.db import models

from user_profile.models import Profile, Teacher


# TO DO check possible inheritance between classes

# Create your models here.

class Lesson(models.Model):
    student = models.ForeignKey(Profile, related_name='student_lessons', on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, related_name='teacher_lessons', on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    date = models.DateTimeField()

    def __str__(self):
        return 'ID: ' + str(self.pk) + ' -> ' + self.subject + ' on ' + str(self.date)


class Availability(models.Model):
    teacher = models.ForeignKey(Teacher, related_name='teacher_availability', on_delete=models.CASCADE)
    date = models.DateTimeField()

    def __str__(self):
        return str(self.date.date()) + ' at ' + str(self.date.time())


class Rating(models.Model):
    student = models.ForeignKey(Profile, related_name='student_rating', on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, related_name='teacher_rating', on_delete=models.CASCADE)
    stars = models.IntegerField(validators=[
            MinValueValidator(0, message=_('Value must be greater than or equal to 0')),
            MaxValueValidator(5, message=_('Value must be less than or equal to 5'))])
