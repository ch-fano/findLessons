# Generated by Django 5.0.6 on 2024-07-04 09:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0008_alter_teacher_teacher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='teacher',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='user_profile.profile'),
        ),
    ]
