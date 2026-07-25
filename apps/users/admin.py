from django.contrib import admin

from .models import CustomerUser


@admin.register(CustomerUser)
class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "email", "name", "created_at")
    search_fields = ("user_id", "email")
