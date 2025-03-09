from django.db.models.signals import post_save
from django.dispatch import receiver
# from guardian.shortcuts import assign_perm
# from django.contrib.auth.models import Group

from .models import LessonCourse, StudentAccessCourse, CoachAccessCourse


# @receiver(post_save, sender=LessonCourse)
# def create_permission_access_course(sender, instance, created, **kwargs):
#     group_course, _ = Group.objects.get_or_create(name=f"course_{instance.course.course_name}")
#     if instance.is_active:
#         for std in instance.students.all():
#             if std.user.groups.filter(name=group_course):
#                 assign_perm("can_view_course", group_course, instance.course)
#             else:
#                 std.user.groups.add(group_course)
#                 assign_perm("can_view_course", group_course, instance.course)


@receiver(post_save, sender=LessonCourse)
def create_student_access_course(sender, instance, created, **kwargs):
    if instance.is_active:
        student_access_course = []
        for std in instance.students.all():
            filter_student_access_course = StudentAccessCourse.objects.filter(student=std, course=instance.course)
            if not filter_student_access_course:
                student_access_course.append(
                    StudentAccessCourse(
                        student=std,
                        course=instance.course
                    )
                )
        StudentAccessCourse.objects.bulk_create(student_access_course)


@receiver(post_save, sender=LessonCourse)
def create_coach_access_course(sender, instance, created, **kwargs):
    if instance.is_active:
        filter_coach_access_course = CoachAccessCourse.objects.filter(coach=instance.coach, course=instance.course)
        if not filter_coach_access_course:
            CoachAccessCourse.objects.create(coach=instance.coach, course=instance.course)
