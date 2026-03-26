from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class  Meta:
        model=Item
        fields = ['title', 'description', 'price_per_day', 'image', 'available']