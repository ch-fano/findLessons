from django.db import models

# TO DO check possible inheritance between classes

# Create your models here.


class Student (models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.EmailField()
    def __str__(self):
        return 'ID: ' + str(self.pk) + ' -> ' + self.name + ' ' + self.surname + ' ' + str(self.email)


class Teacher (models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.EmailField()
    picture = models.ImageField(upload_to='teacher_pictures')
    tel_number = models.CharField(max_length=10)
    subjects = models.TextField()
    address = models.TextField()
    sum_stars = models.IntegerField()
    tot_votes = models.IntegerField()

    def __str__(self):
        return 'ID: ' + str(self.pk) + ' -> ' + self.name + ' ' + self.surname + ' ' + str(self.email)


class Lesson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    date = models.DateField()

    def __str__(self):
        return 'ID: ' + str(self.pk) + ' -> ' + self.subject + ' on ' + self.date




