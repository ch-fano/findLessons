from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from PIL import Image


# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    tel_number = models.CharField(max_length=10, blank=True, default='')
    picture = models.ImageField(default='default_profile.jpg', upload_to='profile_imgs')

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.picture.path)

        if img.height > 250 or img.width > 250:
            new_img = (250, 250)
            img.thumbnail(new_img)
            img.save(self.picture.path)

    def __str__(self):
        return 'ID: ' + str(self.pk) + ' -> ' + self.first_name + ' ' + self.last_name + ' ' + str(self.email)


class Teacher(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    subjects = models.CharField(max_length=100)
    city = models.CharField(max_length=30)
    price = models.IntegerField(null=True,validators=[
            MinValueValidator(0, message=_('Value must be greater than or equal to 0'))])
    stars = models.FloatField(default=0, validators=[
            MinValueValidator(0.0, message=_('Value must be greater than or equal to 0.0')),
            MaxValueValidator(5.0, message=_('Value must be less than or equal to 5.0'))])

    def __str__(self):
        return ('ID: ' + str(self.pk) + ' -> ' + self.city + ' ' + self.subjects+ ' ' + str(self.price) + ' ' +
                str(self.stars))


class Notification(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.profile.first_name} {self.profile.last_name}: {self.message}'

class Request(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    identification = models.ImageField(upload_to='ID_imgs')
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return 'ID: ' + str(self.pk) + ' -> Request from ' + self.first_name + ' ' + self.last_name + ' ' + str(self.email)