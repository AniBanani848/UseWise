from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from items.models import Item

from .forms import RentalRequestForm
from .models import Rental


@login_required
@require_POST
def create_rental(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if item.owner == request.user:
        messages.error(request, "Не можеш да заявиш собствената си вещ.")
        return redirect("item_detail", item_id=item.id)

    form = RentalRequestForm(request.POST, item=item)
    if form.is_valid():
        rental = form.save(commit=False)
        rental.item = item
        rental.renter = request.user
        try:
            rental.full_clean()
        except ValidationError as exc:
            if hasattr(exc, "message_dict"):
                for field, errors in exc.message_dict.items():
                    for error in errors:
                        if field in form.fields:
                            form.add_error(field, error)
                        else:
                            form.add_error(None, error)
            else:
                for error in exc.messages:
                    form.add_error(None, error)
        else:
            rental.save()
            messages.success(request, "Заявката за наем е изпратена.")
            return redirect("rentals:dashboard")

    for errors in form.errors.values():
        for error in errors:
            messages.error(request, error)
    return redirect("item_detail", item_id=item.id)


@login_required
def dashboard(request):
    renter_rentals = Rental.objects.filter(renter=request.user).select_related("item", "item__owner")
    owner_requests = Rental.objects.filter(item__owner=request.user).select_related("item", "renter")
    return render(
        request,
        "rentals/dashboard.html",
        {
            "renter_rentals": renter_rentals,
            "owner_requests": owner_requests,
        },
    )


@login_required
@require_POST
def approve_rental(request, rental_id):
    rental = get_object_or_404(Rental.objects.select_related("item"), pk=rental_id, item__owner=request.user)

    if rental.status != Rental.Status.PENDING:
        messages.error(request, "Само чакащи заявки могат да бъдат одобрени.")
        return redirect("rentals:dashboard")

    rental.status = Rental.Status.APPROVED
    try:
        rental.full_clean()
    except ValidationError as exc:
        rental.status = Rental.Status.PENDING
        for error in exc.messages:
            messages.error(request, error)
    else:
        rental.save(update_fields=["status", "updated_at"])
        messages.success(request, "Заявката е одобрена.")
    return redirect("rentals:dashboard")


@login_required
@require_POST
def decline_rental(request, rental_id):
    rental = get_object_or_404(Rental, pk=rental_id, item__owner=request.user)

    if rental.status != Rental.Status.PENDING:
        messages.error(request, "Само чакащи заявки могат да бъдат отказани.")
        return redirect("rentals:dashboard")

    rental.status = Rental.Status.DECLINED
    rental.save(update_fields=["status", "updated_at"])
    messages.success(request, "Заявката е отказана.")
    return redirect("rentals:dashboard")


@login_required
@require_POST
def cancel_rental(request, rental_id):
    rental = get_object_or_404(Rental, pk=rental_id, renter=request.user)

    if rental.status != Rental.Status.PENDING:
        messages.error(request, "Можеш да отменяш само чакащи заявки.")
        return redirect("rentals:dashboard")

    rental.status = Rental.Status.CANCELLED
    rental.save(update_fields=["status", "updated_at"])
    messages.success(request, "Заявката е отменена.")
    return redirect("rentals:dashboard")
