from django.db import models

from apps.account_app.models import User
from apps.core_app.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from apps.course_app.models import Course


class CourseSignUp(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_signup_one")
    mobile_phone = models.CharField(max_length=15)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    have_account = models.BooleanField(default=False)

    class Meta:
        db_table = "signup_course"

    def save(self, *args, **kwargs):
        if User.objects.filter(mobile_phone=self.mobile_phone).exists():
            self.have_account = True
        super().save(*args, **kwargs)


class Order(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="orders")
    price = models.FloatField()
    mobile_phone = models.CharField(max_length=15)

    class Meta:
        db_table = "order"
