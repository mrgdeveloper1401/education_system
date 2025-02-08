from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.Cart)
class CreateMixinAdmin(admin.ModelAdmin):
    list_display = ['id', "created_at"]
    list_filter = ['created_at']
    list_per_page = 30


@admin.register(models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', "cart", "plan", "created_at", "is_active"]
    list_filter = ['created_at', "is_active"]
    list_select_related = ['cart', 'plan']
    list_per_page = 30
    raw_id_fields = ['cart', "plan"]
    list_display_links = ['id', "cart"]