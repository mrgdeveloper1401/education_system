import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _
import ulid
from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from subscription_app.models import Plan


# Create your models here.


class Cart(CreateMixin, UpdateMixin, SoftDeleteMixin):
    id = models.CharField(max_length=26, primary_key=True, unique=True, editable=False,
                          default=ulid.ULID)

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
