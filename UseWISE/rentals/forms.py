from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Rental


class RentalRequestForm(forms.ModelForm):
    def __init__(self, *args, item=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item

    class Meta:
        model = Rental
        fields = ("start_date", "end_date")
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_start_date(self):
        start_date = self.cleaned_data["start_date"]
        if start_date < timezone.localdate():
            raise ValidationError("Началната дата не може да е в миналото.")
        return start_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if not self.item or not start_date or not end_date:
            return cleaned_data

        overlapping = Rental.overlapping_approved_queryset(
            item=self.item,
            start_date=start_date,
            end_date=end_date,
        ).order_by("start_date")
        if overlapping.exists():
            first_overlap = overlapping.first()
            raise ValidationError(
                f"Вещта вече е заета между {first_overlap.start_date} и {first_overlap.end_date}. "
                "Избери свободни дати."
            )

        return cleaned_data
