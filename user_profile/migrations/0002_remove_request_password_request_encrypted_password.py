# Generated by Django 5.1 on 2024-08-19 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='password',
        ),
        migrations.AddField(
            model_name='request',
            name='encrypted_password',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]
