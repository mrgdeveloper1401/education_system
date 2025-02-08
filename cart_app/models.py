import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _
import ulid
from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from subscription_app.models import Plan


# Create your models here.


class Cart(CreateMixin, UpdateMixin, SoftDeleteMixin):
    is_active = models.BooleanField(default=True)
    id = models.CharField(max_length=26, primary_key=True, unique=True, editable=False,
                          default=ulid.ULID)
    is_added = models.BooleanField(default=False,
                                   help_text=_("ایا به سبد خرید رفته هست یا خیر"))

    def __str__(self):
        return self.id

    @property
    def create_ulid(self):
        return str(ulid.ULID.from_datetime(datetime.datetime.now()))
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            self.id = self.create_ulid
        super().save(*args, **kwargs)

    class Meta:
        db_table = "cart"


class CartItem(CreateMixin, UpdateMixin, SoftDeleteMixin):
    cart = models.ForeignKey(Cart, on_delete=models.DO_NOTHING, related_name='items')
    plan = models.ForeignKey(Plan, on_delete=models.DO_NOTHING, related_name='cart_item_plan')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.cart.id} {self.plan.plan_title}'

    class Meta:
        db_table = "cart_item"


class Order(CreateMixin, UpdateMixin, SoftDeleteMixin):
    cart = models.ForeignKey(Cart, on_delete=models.DO_NOTHING, related_name="order_cart")
    user = models.ForeignKey('accounts.User', on_delete=models.DO_NOTHING, related_name='user_orders')
    is_complete = models.BooleanField(default=False)
    # order_price = models.FloatField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name

    class Meta:
        db_table = 'orders'


class OrderItem(CreateMixin, UpdateMixin, SoftDeleteMixin):
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, related_name='order_items')
    plan = models.ForeignKey("subscription_app.Plan", on_delete=models.DO_NOTHING,
                             related_name="order_item_plan")
    is_active = models.BooleanField(default=True)
    price = models.FloatField()
    final_price = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "order_item"
