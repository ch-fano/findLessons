# Generated by Django 5.0.6 on 2024-06-26 15:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('surname', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('surname', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('picture', models.ImageField(upload_to='teacher_pictures')),
                ('tel_number', models.CharField(max_length=10)),
                ('subjects', models.TextField()),
                ('address', models.TextField()),
                ('sum_stars', models.IntegerField()),
                ('tot_votes', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=50)),
                ('date', models.DateField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.student')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.teacher')),
            ],
        ),
    ]
