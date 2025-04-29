from django.db import models

from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin

class CourseSignUp(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey("course.Course", on_delete=models.PROTECT, related_name="course_singup")
    mobile_phone = models.CharField(max_length=15)
    fist_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return self.mobile_phone

    class Meta:
        db_table = "signup_course"


class Order(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey("course.Course", on_delete=models.PROTECT, related_name="orders")
    price = models.FloatField()
    mobile_phone = models.CharField(max_length=15)

    def __str__(self):
        return self.mobile_phone

    class Meta:
        db_table = "order"
