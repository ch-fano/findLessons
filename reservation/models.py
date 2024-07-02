from django.db import models

from user_profile.models import Profile


# TO DO check possible inheritance between classes

# Create your models here.

class Lesson(models.Model):
    student = models.ForeignKey(Profile, related_name='student_lessons', on_delete=models.CASCADE)
    teacher = models.ForeignKey(Profile, related_name='teacher_lessons', on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    date = models.DateTimeField()

    def __str__(self):
        return 'ID: ' + str(self.pk) + ' -> ' + self.subject + ' on ' + str(self.date)


class Availability(models.Model):
    teacher = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField()


class Rating(models.Model):
    student = models.ForeignKey(Profile, related_name='student_ratings', on_delete=models.CASCADE)
    teacher = models.ForeignKey(Profile, related_name='teacher_ratings', on_delete=models.CASCADE)
    stars = models.IntegerField()


