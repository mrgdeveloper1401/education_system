from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=models.StudentEnrollment)
def add_access_course_student(sender, created, instance, **kwargs):
    if created:
        student, _ = models.AccessCourse.objects.get_or_create(
            user=instance.student.user,
            course=instance.course,
        )


@receiver(post_save, sender=models.CoachEnrollment)
def add_access_course_coach(sender, created, instance, **kwargs):
    if created:
        coach, _ = models.CoachEnrollment.objects.get_or_create(
            user=instance.coach.user,
            course=instance.course,
            is_coach=True,
        )
