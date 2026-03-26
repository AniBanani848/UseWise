from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import ChatMessage, Friendship


User = get_user_model()


def _friendship_between(user_a, user_b):
    return Friendship.objects.filter(
        Q(from_user=user_a, to_user=user_b) | Q(from_user=user_b, to_user=user_a)
    ).first()


@login_required
def contact_list(request):
    friendships = (
        Friendship.objects.filter(Q(from_user=request.user) | Q(to_user=request.user))
        .select_related("from_user", "to_user")
    )

    pending_in = friendships.filter(
        to_user=request.user,
        status=Friendship.Status.PENDING,
    )
    pending_out = friendships.filter(
        from_user=request.user,
        status=Friendship.Status.PENDING,
    )
    accepted = friendships.filter(status=Friendship.Status.ACCEPTED)

    return render(
        request,
        "chat/friends.html",
        {
            "accepted": accepted,
            "pending_in": pending_in,
            "pending_out": pending_out,
        },
    )


@login_required
@require_POST
def add_contact(request):
    identifier = (request.POST.get("email") or "").strip().lower()
    if not identifier:
        messages.error(request, "Въведи имейл.")
        return redirect("chat:list")

    other = User.objects.filter(
        Q(email__iexact=identifier) | Q(username__iexact=identifier)
    ).first()
    if not other:
        messages.error(request, "Няма потребител с такъв имейл.")
        return redirect("chat:list")
    if other.pk == request.user.pk:
        messages.error(request, "Не можеш да започнеш чат със себе си.")
        return redirect("chat:list")

    existing = _friendship_between(request.user, other)
    if existing:
        if existing.status == Friendship.Status.ACCEPTED:
            messages.info(request, "Този чат вече е активен.")
            return redirect("chat:room", friendship_id=existing.pk)

        if existing.to_user_id == request.user.pk:
            existing.status = Friendship.Status.ACCEPTED
            existing.save(update_fields=["status"])
            messages.success(
                request,
                f"Чатът с {other.email} е активиран. Можеш да пишеш веднага.",
            )
            return redirect("chat:room", friendship_id=existing.pk)

        messages.info(request, "Вече си изпратил заявка за чат.")
        return redirect("chat:list")

    Friendship.objects.create(
        from_user=request.user,
        to_user=other,
        status=Friendship.Status.PENDING,
    )
    messages.success(request, f"Изпрати заявка за чат до {other.email}.")
    return redirect("chat:list")


@login_required
@require_POST
def accept_contact(request, pk):
    friendship = get_object_or_404(
        Friendship,
        pk=pk,
        to_user=request.user,
        status=Friendship.Status.PENDING,
    )
    friendship.status = Friendship.Status.ACCEPTED
    friendship.save(update_fields=["status"])
    messages.success(request, "Заявката за чат е приета.")
    return redirect("chat:room", friendship_id=friendship.pk)


@login_required
@require_POST
def decline_contact(request, pk):
    friendship = get_object_or_404(
        Friendship,
        pk=pk,
        to_user=request.user,
        status=Friendship.Status.PENDING,
    )
    friendship.delete()
    messages.info(request, "Заявката за чат е отказана.")
    return redirect("chat:list")


@login_required
def chat_room(request, friendship_id):
    friendship = get_object_or_404(
        Friendship.objects.select_related("from_user", "to_user"),
        pk=friendship_id,
        status=Friendship.Status.ACCEPTED,
    )
    if request.user.pk not in (friendship.from_user_id, friendship.to_user_id):
        raise PermissionDenied()

    chat_messages = list(
        ChatMessage.objects.filter(friendship=friendship)
        .select_related("sender")
        .order_by("-created_at")[:200]
    )
    chat_messages.reverse()

    return render(
        request,
        "chat/room.html",
        {
            "friendship": friendship,
            "other_user": friendship.other_user(request.user),
            "chat_messages": chat_messages,
        },
    )

