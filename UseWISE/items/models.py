from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class Item(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='items/')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class ItemReview(models.Model):
    RATING_CHOICES = [(value, f"{value} / 5") for value in range(1, 6)]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="item_reviews",
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["item", "author"], name="unique_item_review_per_author"),
        ]

    def __str__(self):
        return f"{self.item.title} - {self.rating}/5"

    def clean(self):
        errors = {}

        if self.item_id and self.author_id:
            from rentals.models import Rental

            if self.item.owner_id == self.author_id:
                errors["author"] = "Не можеш да оставиш отзив за собствената си вещ."

            has_completed_rental = Rental.objects.filter(
                item=self.item,
                renter=self.author,
                status=Rental.Status.APPROVED,
                end_date__lt=timezone.localdate(),
            )
            if not has_completed_rental.exists():
                errors["author"] = "Можеш да оставиш отзив само след приключил одобрен наем."

            duplicate_review = ItemReview.objects.filter(item=self.item, author=self.author)
            if self.pk:
                duplicate_review = duplicate_review.exclude(pk=self.pk)
            if duplicate_review.exists():
                errors["author"] = "Вече си оставил отзив за тази вещ."

        if errors:
            raise ValidationError(errors)
