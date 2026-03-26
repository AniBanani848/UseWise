from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from items.models import Item


class Rental(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Изчаква"
        APPROVED = "approved", "Одобрен"
        DECLINED = "declined", "Отказан"
        CANCELLED = "cancelled", "Отказан от наемателя"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="rentals")
    renter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rentals",
    )
    start_date = models.DateField("начална дата")
    end_date = models.DateField("крайна дата")
    status = models.CharField(
        "статус",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.item.title} ({self.start_date} - {self.end_date})"

    @classmethod
    def overlapping_approved_queryset(cls, item, start_date, end_date, exclude_pk=None):
        queryset = cls.objects.filter(
            item=item,
            status=cls.Status.APPROVED,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )
        if exclude_pk is not None:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1

    @property
    def total_price(self):
        return Decimal(self.total_days) * self.item.price_per_day

    @property
    def is_current(self):
        today = timezone.localdate()
        return self.status == self.Status.APPROVED and self.start_date <= today <= self.end_date

    def clean(self):
        errors = {}

        if self.end_date and self.start_date and self.end_date < self.start_date:
            errors["end_date"] = "Крайната дата трябва да е след началната."

        if self.item_id and self.renter_id:
            if self.item.owner_id == self.renter_id:
                errors["renter"] = "Не можеш да наемеш собствената си вещ."

            if not self.item.available:
                errors["item"] = "Тази вещ в момента не е налична за наемане."

        if not errors and self.item_id and self.start_date and self.end_date:
            overlapping = self.overlapping_approved_queryset(
                item=self.item,
                start_date=self.start_date,
                end_date=self.end_date,
                exclude_pk=self.pk,
            )
            if overlapping.exists():
                errors["start_date"] = "Има одобрен наем за част от избрания период."

        if errors:
            raise ValidationError(errors)
