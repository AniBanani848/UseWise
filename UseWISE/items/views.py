from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ItemForm
from .models import Item
from rentals.forms import RentalRequestForm
from rentals.models import Rental

@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()
            return redirect('home')
    else:
        form = ItemForm()

    return render(request, 'add_item.html', {'form': form})

def item_list(request):
    items = Item.objects.all()
    return render(request, 'item_list.html', {'items': items})

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    approved_rentals = Rental.objects.filter(
        item=item,
        status=Rental.Status.APPROVED,
    ).select_related("renter")
    rental_form = None
    if request.user.is_authenticated and request.user != item.owner and item.available:
        rental_form = RentalRequestForm()
    return render(
        request,
        'item_detail.html',
        {
            'item': item,
            'rental_form': rental_form,
            'approved_rentals': approved_rentals,
        },
    )
