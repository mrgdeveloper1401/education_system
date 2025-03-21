from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Section, LessonCourse, StudentAccessSection


@receiver(post_save, sender=LessonCourse)
def create_student_section(sender, instance, created, **kwargs):
    if instance.is_active:
        course = instance.course
        students = instance.students.all()
        course_sections = course.sections.all()

        lst = []

        for i in students:
            for j in course_sections:
                if not StudentAccessSection.objects.filter(student=i, section=j).exists():
                    lst.append(
                        StudentAccessSection(
                            student=i,
                            section=j,
                        )
                    )
        StudentAccessSection.objects.bulk_create(lst)
