from django.templatetags.static import static
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from user_profile.models import Profile
from .models import Chat, Message, Visibility
import re

class BaseTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile

        self.chat = Chat.objects.create()
        self.chat.participants.add(self.profile1, self.profile2)


class ChatModelTestCase(BaseTestCase):
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

class MessageModelTestCase(BaseTestCase):
    def test_message_str_representation(self):
        message = Message.objects.create(chat=self.chat, sender=self.profile1, content="Test Message")
        self.assertEqual(str(message), f'{self.user1.username}: Test Message')

class VisibilityModelTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.visibility = Visibility.objects.get(participant=self.profile1)

    def test_visibility_signals(self):
        self.assertTrue(Visibility.objects.filter(chat=self.chat.pk, participant=self.profile1).exists())
        self.assertTrue(Visibility.objects.filter(chat=self.chat.pk, participant=self.profile2).exists())

    def test_visibility_default(self):
        self.assertTrue(self.visibility.visible)


class ChatViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
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


class ChatTemplateTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='user1', password='password')

    def test_chat_view_template(self):
        response = self.client.get(reverse('chat:chat-view', args=[self.chat.pk]))
        self.assertTemplateUsed(response, 'chat/chat.html')

        # Check for receiver username and chat name in the template
        self.assertContains(response, self.profile2.user.username)
        self.assertContains(response, self.chat.chat_name())
        self.assertContains(response, 'Send')

        # Verify that chat messages are displayed
        message = Message.objects.create(chat=self.chat, sender=self.profile2, content="Test Message")
        response = self.client.get(reverse('chat:chat-view', args=[self.chat.pk]))
        self.assertContains(response, message.content)

    def test_chat_list_rendering(self):
        # Test that the chat list renders correctly with the user's chats
        chat2 = Chat.objects.create()
        chat2.participants.add(self.profile1)
        chat2.participants.add(User.objects.create_user(username='user3', password='password').profile)

        response = self.client.get(reverse('chat:chat-view', args=[self.chat.pk]))
        self.assertContains(response, self.profile2.user.username)
        self.assertNotContains(response, 'No chats available')

        # Test for an empty chat list scenario
        Chat.objects.filter(participants=self.profile1).delete()
        response = self.client.get(reverse('chat:chat-home'))
        self.assertContains(response, 'No chats available')

    def test_message_input_visibility(self):
        # Test that the message input box and send button are visible when a receiver is present
        response = self.client.get(reverse('chat:chat-view', args=[self.chat.pk]))
        self.assertContains(response, '<textarea id="chat-message-input" type="text"></textarea>', html=True)
        self.assertContains(response, '<button id="chat-message-submit">Send</button>', html=True)

    def test_no_receiver(self):
        # Test that the input and button do not appear if no receiver is set
        chat_with_no_receiver = Chat.objects.create()
        chat_with_no_receiver.participants.add(self.profile1)

        # Initial request to check if it redirects
        response = self.client.get(reverse('chat:chat-view', args=[chat_with_no_receiver.pk]))

        # Ensure it was redirected
        self.assertEqual(response.status_code, 302)

        # Follow the redirect to the final page
        follow_response = self.client.get(response['Location'], follow=True)

        # Ensure the final status code after following the redirect is 200
        self.assertEqual(follow_response.status_code, 200)

        # Check that the input and button do not appear on the final page
        self.assertNotContains(follow_response, '<textarea id="chat-message-input" type="text"></textarea>', html=True)
        self.assertNotContains(follow_response, '<button id="chat-message-submit">Send</button>', html=True)

    def test_chat_delete_link(self):
        # Test that the delete button is displayed and links correctly
        response = self.client.get(reverse('chat:chat-view', args=[self.chat.pk]))
        delete_url = reverse('chat:chat-delete', args=[self.chat.pk])
        delete_img_path = static('imgs/delete.png')
        self.assertContains(response, f'<a href="{delete_url}"><img src="{delete_img_path}" class="delete-img" alt="Delete"></a>', html=True)

    def test_receiver_profile_link(self):
        # Test that the receiver's profile link is correct
        response = self.client.get(reverse('chat:chat-view', args=[self.chat.pk]))

        profile_url = reverse('user_profile:view-profile', args=[self.profile2.pk]) + "?source=chat"
        pattern = re.compile(r'href="{}"'.format(re.escape(profile_url)))

        self.assertTrue(pattern.search(response.content.decode('utf-8')))

    def test_message_display(self):
        # Test that messages are displayed with the correct class based on the sender
        message1 = Message.objects.create(chat=self.chat, sender=self.profile1, content="Message from user1")
        message2 = Message.objects.create(chat=self.chat, sender=self.profile2, content="Message from user2")

        response = self.client.get(reverse('chat:chat-view', args=[self.chat.pk]))
        self.assertContains(response, 'message-box sent')
        self.assertContains(response, 'message-box received')
        self.assertContains(response, message1.content)
        self.assertContains(response, message2.content)

    def test_websocket_setup(self):
        # Test that the WebSocket setup script is included in the response
        response = self.client.get(reverse('chat:chat-view', args=[self.chat.pk]))
        self.assertContains(response, "const chatName =")
        self.assertContains(response, "const username =")
        self.assertContains(response, "setupWebSocket()")
