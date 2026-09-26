from django.contrib import admin
from .models import Category,Products,Order


admin.site.register(Category)
admin.site.register(Products)
#admin.site.register(Order)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "amount", "status", "mpesa_receipt", "created_at"]
    list_filter = ["status"]


# Register your models here.
