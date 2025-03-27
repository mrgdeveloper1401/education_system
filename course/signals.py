from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import LessonCourse, StudentAccessSection


@receiver(m2m_changed, sender=LessonCourse.students.through)
def handle_student_changes(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        course = instance.course
        students = instance.students.filter(id__in=pk_set)
        sections = course.sections.filter(is_publish=True)

        access_list = [
            StudentAccessSection(student=student, section=section)
            for student in students
            for section in sections
            if not StudentAccessSection.objects.filter(
                student=student,
                section=section
            ).exists()
        ]
        StudentAccessSection.objects.bulk_create(access_list)


@receiver(m2m_changed, sender=LessonCourse.students.through)
def student_access_section(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        std_access = StudentAccessSection.objects.filter(
            student_id__in=pk_set,
            section__course=instance.course,
            section__is_publish=True,
            section__course__is_publish=True
        ).order_by('created_at').first()

        if std_access:
            std_access.is_access = True
            std_access.save()


@receiver(m2m_changed, sender=LessonCourse.students.through)
def remove_access_student(sender, instance, action, pk_set, **kwargs):
    if action == "post_remove":
        StudentAccessSection.objects.filter(
            student_id__in=pk_set,
            section__course=instance.course,
            is_access=True,
        ).update(is_access=False)
