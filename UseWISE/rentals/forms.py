from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Rental


class RentalRequestForm(forms.ModelForm):
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
