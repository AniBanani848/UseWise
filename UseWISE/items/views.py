from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone

from .forms import ItemForm, ItemReviewForm
from .models import Item, ItemReview
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
    query = request.GET.get('q', '').strip()
    items = Item.objects.annotate(
        average_rating=Avg("reviews__rating"),
        review_count=Count("reviews"),
    )
    if query:
        items = items.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'item_list.html', {'items': items, 'query': query})

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    approved_rentals = Rental.objects.filter(
        item=item,
        status=Rental.Status.APPROVED,
    ).select_related("renter")
    rental_form = None
    reviews = item.reviews.select_related("author")
    review_summary = reviews.aggregate(
        average_rating=Avg("rating"),
        review_count=Count("id"),
    )
    can_review = False
    has_user_review = False
    review_form = None
    if request.user.is_authenticated and request.user != item.owner and item.available:
        rental_form = RentalRequestForm(item=item)

    if request.user.is_authenticated and request.user != item.owner:
        has_user_review = reviews.filter(author=request.user).exists()
        can_review = Rental.objects.filter(
            item=item,
            renter=request.user,
            status=Rental.Status.APPROVED,
            end_date__lt=timezone.localdate(),
        ).exists() and not has_user_review
        if can_review:
            review_form = ItemReviewForm()

    return render(
        request,
        'item_detail.html',
        {
            'item': item,
            'rental_form': rental_form,
            'approved_rentals': approved_rentals,
            'reviews': reviews,
            'review_summary': review_summary,
            'review_form': review_form,
            'can_review': can_review,
            'has_user_review': has_user_review,
        },
    )


@login_required
@require_POST
def add_review(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    form = ItemReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit=False)
        review.item = item
        review.author = request.user
        try:
            review.full_clean()
        except ValidationError as exc:
            for errors in exc.message_dict.values():
                for error in errors:
                    messages.error(request, error)
        else:
            review.save()
            messages.success(request, "Благодарим ти за отзива.")
            return redirect("item_detail", item_id=item.id)

    for errors in form.errors.values():
        for error in errors:
            messages.error(request, error)
    return redirect("item_detail", item_id=item.id)
