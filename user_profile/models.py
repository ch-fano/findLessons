from django.contrib.auth.models import User
from django.db import models
from PIL import Image


# Create your models here.


class Profile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
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


class Teacher (models.Model):
    teacher = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tel_number = models.CharField(max_length=10)
    subjects = models.TextField()
    city = models.TextField()
    stars = models.FloatField(default=0)
