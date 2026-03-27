from django import forms

from .models import Item, ItemReview

class ItemForm(forms.ModelForm):
    class  Meta:
        model=Item
        fields = ['title', 'description', 'price_per_day', 'image', 'available']


class ItemReviewForm(forms.ModelForm):
    class Meta:
        model = ItemReview
        fields = ["rating", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Как мина наемът и какво мислиш за вещта?"}),
        }
        labels = {
            "rating": "Оценка",
            "comment": "Отзив",
        }
