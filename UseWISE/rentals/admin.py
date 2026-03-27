from django.contrib import admin

from .models import Rental


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ("item", "renter", "start_date", "end_date", "status", "created_at")
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("item__title", "renter__email", "item__owner__email")
