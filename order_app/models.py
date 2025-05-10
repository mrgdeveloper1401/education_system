from django.db import models

from accounts.models import User
from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin

class CourseSignUp(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey("course.Course", on_delete=models.PROTECT, related_name="course_signup_one")
    mobile_phone = models.CharField(max_length=15)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    have_account = models.BooleanField(default=False)

    def __str__(self):
        return self.mobile_phone

    class Meta:
        db_table = "signup_course"

    def save(self, *args, **kwargs):
        if User.objects.filter(mobile_phone=self.mobile_phone).exists():
            self.have_account = True
        super().save(*args, **kwargs)


class Order(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey("course.Course", on_delete=models.PROTECT, related_name="orders")
    price = models.FloatField()
    mobile_phone = models.CharField(max_length=15)

    def __str__(self):
        return self.mobile_phone

    class Meta:
        db_table = "order"


# class Payment(CreateMixin, UpdateMixin, SoftDeleteMixin):
#     course = models.ForeignKey("course.Course", on_delete=models.PROTECT, related_name="course_payments")
#     price = models.FloatField()
#     user = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="user_payments")
#
#     def __str__(self):
#         return f'{self.user.mobile_phone} {self.price}'
#
#     class Meta:
#         db_table = "payment"
