from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Friendship


User = get_user_model()


class ChatFlowTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.alice = User.objects.create_user(
            email="alice@example.com",
            password=self.password,
            first_name="Alice",
            last_name="A",
            country="Bulgaria",
            city_or_village="Sofia",
            phone="+359888200001",
            is_active=True,
        )
        self.bob = User.objects.create_user(
            email="bob@example.com",
            password=self.password,
            first_name="Bob",
            last_name="B",
            country="Bulgaria",
            city_or_village="Varna",
            phone="+359888200002",
            is_active=True,
        )
        self.carol = User.objects.create_user(
            email="carol@example.com",
            password=self.password,
            first_name="Carol",
            last_name="C",
            country="Bulgaria",
            city_or_village="Plovdiv",
            phone="+359888200003",
            is_active=True,
        )

    def test_add_contact_creates_pending_request(self):
        self.client.force_login(self.alice)

        response = self.client.post(
            reverse("chat:add_contact"),
            {"email": self.bob.email},
        )

        friendship = Friendship.objects.get()
        self.assertRedirects(response, reverse("chat:list"))
        self.assertEqual(friendship.from_user, self.alice)
        self.assertEqual(friendship.to_user, self.bob)
        self.assertEqual(friendship.status, Friendship.Status.PENDING)

    def test_reverse_pending_request_is_auto_accepted(self):
        friendship = Friendship.objects.create(
            from_user=self.bob,
            to_user=self.alice,
            status=Friendship.Status.PENDING,
        )
        self.client.force_login(self.alice)

        response = self.client.post(
            reverse("chat:add_contact"),
            {"email": self.bob.email},
        )

        friendship.refresh_from_db()
        self.assertRedirects(response, reverse("chat:room", args=[friendship.pk]))
        self.assertEqual(friendship.status, Friendship.Status.ACCEPTED)

    def test_direct_start_opens_chat_immediately(self):
        self.client.force_login(self.alice)

        response = self.client.post(
            reverse("chat:start_direct", args=[self.bob.pk]),
        )

        friendship = Friendship.objects.get()
        self.assertRedirects(response, reverse("chat:room", args=[friendship.pk]))
        self.assertEqual(friendship.status, Friendship.Status.ACCEPTED)

    def test_only_participants_can_open_chat_room(self):
        friendship = Friendship.objects.create(
            from_user=self.alice,
            to_user=self.bob,
            status=Friendship.Status.ACCEPTED,
        )
        self.client.force_login(self.carol)

        response = self.client.get(reverse("chat:room", args=[friendship.pk]))

        self.assertEqual(response.status_code, 403)
