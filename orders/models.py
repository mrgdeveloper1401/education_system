from django.db import models

from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin


class Order(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey('accounts.User', on_delete=models.DO_NOTHING, related_name='user_orders')
    course = models.ForeignKey('course.Course', related_name='course_orders', on_delete=models.DO_NOTHING)
    price = models.FloatField()
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.get_full_name} {self.course.course_name}'

    class Meta:
        db_table = 'orders'


# class Transaction(CreateMixin, UpdateMixin, SoftDeleteMixin):
#     pass