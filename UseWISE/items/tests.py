from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rentals.models import Rental

from .models import Item, ItemReview


User = get_user_model()


class ItemReviewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123!",
            first_name="Owner",
            last_name="User",
            country="Bulgaria",
            city_or_village="Sofia",
            phone="+359888200001",
            is_active=True,
        )
        self.renter = User.objects.create_user(
            email="renter@example.com",
            password="StrongPass123!",
            first_name="Renter",
            last_name="User",
            country="Bulgaria",
            city_or_village="Plovdiv",
            phone="+359888200002",
            is_active=True,
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="StrongPass123!",
            first_name="Other",
            last_name="User",
            country="Bulgaria",
            city_or_village="Varna",
            phone="+359888200003",
            is_active=True,
        )
        self.item = Item.objects.create(
            owner=self.owner,
            title="Стълба",
            description="Стабилна алуминиева стълба.",
            price_per_day="8.50",
            image="items/ladder.jpg",
            available=True,
        )
        self.completed_rental = Rental.objects.create(
            item=self.item,
            renter=self.renter,
            start_date=timezone.localdate() - timedelta(days=5),
            end_date=timezone.localdate() - timedelta(days=2),
            status=Rental.Status.APPROVED,
        )

    def test_completed_renter_can_leave_review(self):
        self.client.force_login(self.renter)

        response = self.client.post(
            reverse("add_review", args=[self.item.id]),
            {"rating": 5, "comment": "Много полезна вещ и отлична комуникация."},
            follow=True,
        )

        self.assertRedirects(response, reverse("item_detail", args=[self.item.id]))
        review = ItemReview.objects.get()
        self.assertEqual(review.item, self.item)
        self.assertEqual(review.author, self.renter)
        self.assertContains(response, "Благодарим ти за отзива.")

    def test_user_without_completed_rental_cannot_leave_review(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("add_review", args=[self.item.id]),
            {"rating": 4, "comment": "Опит за отзив."},
            follow=True,
        )

        self.assertEqual(ItemReview.objects.count(), 0)
        self.assertContains(response, "Можеш да оставиш отзив само след приключил одобрен наем.")

    def test_user_cannot_leave_second_review_for_same_item(self):
        ItemReview.objects.create(
            item=self.item,
            author=self.renter,
            rating=5,
            comment="Първи отзив.",
        )
        self.client.force_login(self.renter)

        response = self.client.post(
            reverse("add_review", args=[self.item.id]),
            {"rating": 3, "comment": "Втори отзив."},
            follow=True,
        )

        self.assertEqual(ItemReview.objects.count(), 1)
        self.assertContains(response, "Вече си оставил отзив за тази вещ.")

    def test_item_detail_shows_review_summary(self):
        ItemReview.objects.create(
            item=self.item,
            author=self.renter,
            rating=4,
            comment="Добре поддържана вещ.",
        )

        response = self.client.get(reverse("item_detail", args=[self.item.id]))

        self.assertContains(response, "4,0/5 от 1 отзива")
        self.assertContains(response, "Добре поддържана вещ.")
