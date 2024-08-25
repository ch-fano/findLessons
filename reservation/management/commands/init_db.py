from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.core.files import File
from user_profile.models import Profile, Teacher, Request, Notification
from reservation.models import Lesson, Availability, Rating
from chat.models import Chat, Message, Visibility
from datetime import datetime, timedelta
from django.utils import timezone
import random
import os


class Command(BaseCommand):
    help = 'Initializes the database with sample data'

    def handle(self, *args, **kwargs):
        self.erase_db()
        self.delete_imgs()
        self.init_db()

    def erase_db(self):
        admin_user = User.objects.filter(is_superuser=True).first()

        User.objects.exclude(is_superuser=True).delete()
        Profile.objects.exclude(user=admin_user).delete()
        Teacher.objects.all().delete()
        Lesson.objects.all().delete()
        Availability.objects.all().delete()
        Rating.objects.all().delete()
        Notification.objects.all().delete()
        Request.objects.all().delete()
        Chat.objects.all().delete()
        Message.objects.all().delete()
        Visibility.objects.all().delete()

    def delete_imgs(self):
        dirs = ['./././media/profile_imgs', './././media/ID_imgs']

        for imgs_path in dirs:
            for img in os.listdir(imgs_path):
                os.remove(os.path.join(imgs_path, img))

    def get_random_date(self, hour, future=True):
        days = random.randint(0, 14)
        if future:
            date = datetime.now() + timedelta(days=days)
        else:
            date = datetime.now() - timedelta(days=days)
        return timezone.make_aware(date.replace(hour=hour, minute=00, second=0, microsecond=0))

    def set_profile(self, user, name, surname, photo_path):
        profile = Profile.objects.get(user=user)

        with open(photo_path, 'rb') as image_file:
            profile.picture.save(os.path.basename(photo_path), File(image_file))

        profile.first_name = name
        profile.last_name = surname
        profile.email = f'{name.lower()}.{surname.lower()}@gmail.com'
        profile.save()

    def set_teacher(self, user):
        cities = ['Modena', 'Bologna', 'Parma']
        subjects = ['Matematica', 'Italiano', 'Inglese', 'Latino', 'Greco', 'Fisica', 'Informatica']
        price_min = 15

        teacher, _ = Teacher.objects.get_or_create(profile=user.profile)
        teacher.city = random.choice(cities)
        teacher.subjects = random.choice(subjects)

        for _ in range(random.randint(0, 3)):
            subject = random.choice(subjects)
            if subject not in teacher.subjects:
                teacher.subjects = teacher.subjects + ', ' + subject

        teacher.price = price_min + random.randint(0, 20)
        teacher.save()

    def set_availability(self, user):
        hours = [10, 12, 14, 17, 19]

        for _ in range(random.randint(2, 7)):
            date = self.get_random_date(random.choice(hours))

            if not Availability.objects.filter(teacher=user.profile.teacher, date=date).exists():
                availability = Availability(teacher=user.profile.teacher, date=date)
                availability.save()

    def set_lesson(self, student, teacher):
        hours = [8, 11, 15, 16, 18]

        for _ in range(random.randint(1, 5)):
            if random.random() <= 0.3:
                date = self.get_random_date(random.choice(hours), future=False)
            else:
                date = self.get_random_date(random.choice(hours), future=True)

            subject = random.choice(teacher.subjects.replace(',', '').split())

            if (not Lesson.objects.filter(teacher=teacher, date=date).exists() and
                    not Lesson.objects.filter(student=student, date=date).exists()):
                lesson = Lesson(student=student, teacher=teacher, subject=subject, date=date)
                lesson.save()

    def set_rating(self, student, teacher):
        if not Rating.objects.filter(student=student, teacher=teacher).exists():
            rating = Rating(student=student, teacher=teacher, stars=random.randint(0, 5))
            rating.save()

    def set_request(self):
        users_dict = {
            'username': ['bianca.rossi', 'valentino.blu'],
            'first_name': ['Bianca', 'Valentino'],
            'last_name': ['Rossi', 'Blu'],
            'email': ['bianca.rossi@gmail.com', 'valentino.blu@gmail.com'],
            'ID': ['./././static/init_imgs/ID/ID_female.png', './././static/init_imgs/ID/ID_male.png']
        }

        for i in range(2):
            request = Request(username=users_dict['username'][i], first_name=users_dict['first_name'][i],
                             last_name=users_dict['last_name'][i], email=users_dict['email'][i])

            with open(users_dict['ID'][i], 'rb') as image_file:
                request.identification.save(os.path.basename(users_dict['ID'][i]), File(image_file))

            request.set_password('superciao')
            request.save()

    def init_db(self):
        if len(User.objects.all()) != 1:
            return

        names = ['Leonardo', 'Francesco', 'Tommaso', 'Edoardo', 'Alessandro', 'Sofia', 'Aurora', 'Giulia', 'Ginevra',
                 'Vittoria', 'Lorenzo', 'Martino', 'Gabriele', 'Riccardo', 'Marco', 'Alessio', 'Luigi', 'Giulio',
                 'Roberto', 'Marcello', 'Rita', 'Anita', 'Ludovica', 'Emma', 'Matilda', 'Roberta', 'Silvia',
                 'Barbara', 'Margherita', 'Silvana']

        surnames = ['Rossi', 'Ferrari', 'Russo', 'Esposito', 'Bianchi', 'Romano', 'Gallo', 'Costa', 'Fontana', 'Conti',
                    'Ricci', 'Bruno', 'Moretti', 'Marino', 'Greco', 'Barbieri', 'Lombardi', 'Giordano', 'Cassano',
                    'Colombo', 'Mancini', 'Longo', 'Leone', 'Martinelli', 'Matera', 'Cotti', 'Govoni', 'Marchetti',
                    'Martini', 'Gatti']

        male_dir = './././static/init_imgs/male'
        female_dir = './././static/init_imgs/female'

        student_male = [os.path.join(male_dir + '/student/', f) for f in os.listdir(male_dir + '/student/')]
        student_female = [os.path.join(female_dir + '/student/', f) for f in os.listdir(female_dir + '/student/')]

        teacher_male = [os.path.join(male_dir + '/teacher/', f) for f in os.listdir(male_dir + '/teacher/')]
        teacher_female = [os.path.join(female_dir + '/teacher/', f) for f in os.listdir(female_dir + '/teacher/')]

        students_group, _ = Group.objects.get_or_create(name='Students')
        teachers_group, _ = Group.objects.get_or_create(name='Teachers')

        num_students = 10
        for name in names:
            surname = surnames.pop()

            username = f'{name.lower()}.{surname.lower()}'
            user = User(username=username)
            user.set_password('superciao')
            user.save()

            print(username)
            if num_students > 0:
                user.groups.add(students_group)
                photo = student_female if name[-1] == 'a' else student_male

                num_students -= 1
            else:
                user.groups.add(teachers_group)

                photo = teacher_female if name[-1] == 'a' else teacher_male
                self.set_teacher(user)
                self.set_availability(user)

            self.set_profile(user, name, surname, photo.pop())

        students = students_group.user_set.all()
        teachers = teachers_group.user_set.all()

        for teacher_user in teachers:
            for _ in range(random.randint(1, 4)):
                student_user = random.choice(students)
                self.set_lesson(student_user.profile, teacher_user.profile.teacher)
                self.set_rating(student_user.profile, teacher_user.profile.teacher)

        self.set_request()

