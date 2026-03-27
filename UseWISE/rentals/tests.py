from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from items.models import Item

from .models import Rental


User = get_user_model()


class RentalFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123!",
            first_name="Owner",
            last_name="User",
            country="Bulgaria",
            city_or_village="Sofia",
            phone="+359888100001",
            is_active=True,
        )
        self.renter = User.objects.create_user(
            email="renter@example.com",
            password="StrongPass123!",
            first_name="Renter",
            last_name="User",
            country="Bulgaria",
            city_or_village="Plovdiv",
            phone="+359888100002",
            is_active=True,
        )
        self.second_renter = User.objects.create_user(
            email="second@example.com",
            password="StrongPass123!",
            first_name="Second",
            last_name="Renter",
            country="Bulgaria",
            city_or_village="Varna",
            phone="+359888100003",
            is_active=True,
        )
        self.item = Item.objects.create(
            owner=self.owner,
            title="Бормашина",
            description="Ударна бормашина за домашни ремонти.",
            price_per_day="12.50",
            image="items/drill.jpg",
            available=True,
        )
        self.start_date = timezone.localdate() + timedelta(days=2)
        self.end_date = self.start_date + timedelta(days=2)

    def test_renter_can_create_rental_request(self):
        self.client.force_login(self.renter)

        response = self.client.post(
            reverse("rentals:create", args=[self.item.id]),
            {"start_date": self.start_date, "end_date": self.end_date},
        )

        rental = Rental.objects.get()
        self.assertRedirects(response, reverse("rentals:dashboard"))
        self.assertEqual(rental.item, self.item)
        self.assertEqual(rental.renter, self.renter)
        self.assertEqual(rental.status, Rental.Status.PENDING)

    def test_owner_cannot_request_own_item(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("rentals:create", args=[self.item.id]),
            {"start_date": self.start_date, "end_date": self.end_date},
        )

        self.assertRedirects(response, reverse("item_detail", args=[self.item.id]))
        self.assertFalse(Rental.objects.exists())

    def test_owner_can_approve_pending_request(self):
        rental = Rental.objects.create(
            item=self.item,
            renter=self.renter,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        self.client.force_login(self.owner)

        response = self.client.post(reverse("rentals:approve", args=[rental.id]))

        rental.refresh_from_db()
        self.assertRedirects(response, reverse("rentals:dashboard"))
        self.assertEqual(rental.status, Rental.Status.APPROVED)

    def test_overlapping_approved_rental_is_rejected(self):
        Rental.objects.create(
            item=self.item,
            renter=self.renter,
            start_date=self.start_date,
            end_date=self.end_date,
            status=Rental.Status.APPROVED,
        )
        self.client.force_login(self.second_renter)

        response = self.client.post(
            reverse("rentals:create", args=[self.item.id]),
            {
                "start_date": self.start_date + timedelta(days=1),
                "end_date": self.end_date + timedelta(days=1),
            },
        )

        self.assertRedirects(response, reverse("item_detail", args=[self.item.id]))
        self.assertEqual(Rental.objects.count(), 1)

    def test_same_day_overlap_with_approved_rental_is_rejected(self):
        Rental.objects.create(
            item=self.item,
            renter=self.renter,
            start_date=self.start_date,
            end_date=self.end_date,
            status=Rental.Status.APPROVED,
        )
        self.client.force_login(self.second_renter)

        response = self.client.post(
            reverse("rentals:create", args=[self.item.id]),
            {
                "start_date": self.end_date,
                "end_date": self.end_date + timedelta(days=2),
            },
            follow=True,
        )

        self.assertContains(response, "Вещта вече е заета между")
        self.assertEqual(Rental.objects.count(), 1)

    def test_dashboard_shows_renter_and_owner_sections(self):
        rental = Rental.objects.create(
            item=self.item,
            renter=self.renter,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        self.client.force_login(self.owner)
        response = self.client.get(reverse("rentals:dashboard"))

        self.assertContains(response, "Заявки към моите вещи")
        self.assertContains(response, rental.item.title)
        self.assertContains(response, rental.renter.first_name)
