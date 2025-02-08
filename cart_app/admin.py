from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Cart)
class CreateMixinAdmin(admin.ModelAdmin):
    list_display = ['id', "is_added", "created_at", "is_active"]
    list_filter = ['created_at', "is_active"]
    list_per_page = 30


@admin.register(models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', "cart", "plan", "created_at", "is_active"]
    list_filter = ['created_at', "is_active"]
    list_select_related = ['cart', 'plan']
    list_per_page = 30
    raw_id_fields = ['cart', "plan"]
    list_display_links = ['id', "cart"]


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', "cart", "is_complete", "is_active"]
    list_select_related = ['user', "cart"]
    list_filter = ['is_complete', "created_at", "is_active"]
    raw_id_fields = ['user', "cart"]
    list_per_page = 20


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', "plan", "is_active", "created_at"]
    list_select_related = ['order', "plan"]
    search_fields = ['plan__plan_title']
    list_filter = ['is_active', "created_at"]
