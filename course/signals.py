from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .models import StudentEnrollment, TeacherEnrollment
from subscription_app.models import AccessCourse


@receiver(post_save, sender=StudentEnrollment)
def access_course_student(sender, created, instance, **kwargs):
    access_course, cr = AccessCourse.objects.get_or_create(course=instance.course, user=instance.student.user)
    if cr is False:
        if instance.status == "dropped":
            AccessCourse.objects.filter(user=instance.student.user, course=instance.course).update(is_active=False)
        if instance.status == "active":
            AccessCourse.objects.filter(user=instance.student.user, course=instance.course).update(is_active=True)


# @receiver(post_delete, sender=StudentEnrollment)
# def update_field_course_student(sender, instance, **kwargs):
#     print("post_delete signals")
#     AccessCourse.objects.filter(user=instance.student.user, course=instance.course).update(is_active=False)


@receiver(post_save, sender=TeacherEnrollment)
def access_course_coach(sender, created, instance, **kwargs):
    AccessCourse.objects.get_or_create(course=instance.course, user=instance.coach.user)


@receiver(post_delete, sender=TeacherEnrollment)
def update_field_course_coach(sender, instance, **kwargs):
    AccessCourse.objects.filter(user=instance.coach.user, course=instance.course).update(is_active=False)
