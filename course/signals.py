from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import LessonCourse, Purchases


@receiver(post_save, sender=LessonCourse)
def create_access_course(sender, instance, created, **kwargs):
    if instance.is_active:
        students = instance.students.all()
        student_list = []
        for student in students:
            if not Purchases.objects.filter(user=student.user, course=instance.course).exists():
                student_list.append(
                    Purchases(user=student.user, course=instance.course, coach=instance.coach)
                )
        if student_list:
            Purchases.objects.bulk_create(student_list)
