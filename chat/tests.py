from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from user_profile.models import Profile
from .models import Chat, Message, Visibility


class ChatModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile

        self.chat = Chat.objects.create()
        self.chat.participants.add(self.profile1, self.profile2)

    def test_chat_name(self):
        self.assertEqual(self.chat.chat_name(), f'chat_{self.chat.pk}')

    def test_get_other_participant(self):
        other = self.chat.get_other_participant(self.profile1)
        self.assertEqual(other, self.profile2)

        unknown = self.chat.get_other_participant(Profile())
        self.assertEqual(unknown, None)

    def test_has_new_messages(self):
        message = Message.objects.create(chat=self.chat, sender=self.profile2, content="Test")
        self.assertTrue(self.chat.has_new_messages(self.profile1))

        message.read = True
        message.save()
        self.assertFalse(self.chat.has_new_messages(self.profile1))

    def test_read_messages(self):
        message = Message.objects.create(chat=self.chat, sender=self.profile2, content="Test", read=False)
        self.chat.read_messages(self.profile1)
        message.refresh_from_db()
        self.assertTrue(message.read)

    def test_str_representation(self):
        self.assertEqual(str(self.chat), f'Chat between {self.user1.username},{self.user2.username}')

class MessageModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.profile1 = self.user1.profile
        self.chat = Chat.objects.create()
        self.chat.participants.add(self.profile1)

    def test_message_str_representation(self):
        message = Message.objects.create(chat=self.chat, sender=self.profile1, content="Test Message")
        self.assertEqual(str(message), f'{self.user1.username}: Test Message')

class VisibilityModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.profile1 = self.user1.profile
        self.chat = Chat.objects.create()
        self.visibility = Visibility.objects.create(chat=self.chat, participant=self.profile1)

    def test_visibility_default(self):
        self.assertTrue(self.visibility.visible)


class ChatViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        self.client.login(username='user1', password='password')

    def test_start_chat(self):
        response = self.client.post(reverse('chat:chat-start', args=[self.profile2.pk]))
        chat = Chat.objects.filter(participants=self.profile1).filter(participants=self.profile2).first()
        self.assertRedirects(response, reverse('chat:chat-view', args=[chat.pk]))

    def test_start_chat_self(self):
        response = self.client.post(reverse('chat:chat-start', args=[self.profile1.pk]))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'You cannot chat with yourself')

    def test_chat_view_access(self):
        chat = Chat.objects.create()
        chat.participants.add(self.profile1, self.profile2)

        response = self.client.get(reverse('chat:chat-view', args=[chat.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat.html')

    def test_chat_view_forbidden(self):
        chat = Chat.objects.create()
        chat.participants.add(self.profile2)
        response = self.client.get(reverse('chat:chat-view', args=[chat.pk]))
        self.assertEqual(response.status_code, 403)


    def test_chat_delete(self):
        chat = Chat.objects.create()
        chat.participants.add(self.profile1, self.profile2)
        chat_pk = chat.pk
        visibility1 = Visibility.objects.get(chat=chat, participant=self.profile1)

        response = self.client.post(reverse('chat:chat-delete', args=[chat.pk]))
        visibility1.refresh_from_db()
        self.assertFalse(visibility1.visible)
        self.assertRedirects(response, reverse('chat:chat-home'))

        self.client.login(username='user2', password='password')
        response = self.client.post(reverse('chat:chat-delete', args=[chat.pk]))

        self.assertFalse(Chat.objects.filter(pk=chat_pk).exists())

        self.assertRedirects(response, reverse('chat:chat-home'))

    def test_chat_home(self):
        response = self.client.get(reverse('chat:chat-home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat.html')


class ChatTemplateTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        self.client.login(username='user1', password='password')

        self.chat = Chat.objects.create()
        self.chat.participants.add(self.profile1, self.profile2)

    def test_chat_view_template(self):
        response = self.client.get(reverse('chat:chat-view', args=[self.chat.pk]))
        self.assertTemplateUsed(response, 'chat/chat.html')

        self.assertContains(response, self.profile2.user.username)
        self.assertContains(response, self.chat.chat_name())
        self.assertContains(response, 'Send')

        # Verify chat messages are displayed
        message = Message.objects.create(chat=self.chat, sender=self.profile2, content="Test Message")
        response = self.client.get(reverse('chat:chat-view', args=[self.chat.pk]))
        self.assertContains(response, message.content)
