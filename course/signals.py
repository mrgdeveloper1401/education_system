from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from accounts.models import PrivateNotification, User
from .enums import SendFileChoices
from .models import LessonCourse, StudentAccessSection, SendSectionFile, CallLessonCourse, StudentEnrollment, Section


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


@receiver(post_save, sender=SendSectionFile)
def next_section_access(sender, instance, **kwargs):
    if instance.send_file_status == SendFileChoices.accepted and instance.score > 60:
        get_student_section_access = StudentAccessSection.objects.filter(
            student=instance.student,
            section=instance.section_file.section
        ).first()

        if get_student_section_access:
            StudentAccessSection.objects.filter(id=get_student_section_access.id + 1).update(
                is_access=True,
            )


@receiver(post_save, sender=SendSectionFile)
def send_notification_when_score_is_accepted(sender, instance, **kwargs):
    if instance.score:
        PrivateNotification.objects.create(
            user=instance.students.user,
            body="دانشجوی محترم نمره شما ثبت و ویرایش شده هست"
        )


@receiver(post_save, sender=CallLessonCourse)
def create_admin_notification_when_cancel_student(sender, instance, created, **kwargs):
    if instance.cancellation_alert:
        admin_user = User.objects.filter(is_staff=True).only("is_staff")
        lst = [
            PrivateNotification(
                user=i,
                title='cancel student',
                body="please check student, this he want cancel"
            )
            for i in admin_user
        ]

        if lst:
            PrivateNotification.objects.bulk_create(lst)


@receiver(post_save, sender=StudentEnrollment)
def access_student_access_section(sender, instance, created, **kwargs):
    if created:
        # بررسی آیا دانش‌آموز قبلاً سکشن‌هایی دارد یا نه
        existing_sections = StudentAccessSection.objects.filter(
            student=instance.student
        ).exists()

        lesson_course_sections = instance.lesson_course.course.sections.filter(is_publish=True)

        create_student_access_section = []
        for index, section in enumerate(lesson_course_sections):
            # اگر اولین سکشن باشد و دانش‌آموز هیچ سکشن دیگری نداشته باشد
            is_access = index == 0 and not existing_sections
            create_student_access_section.append(
                StudentAccessSection(
                    section=section,
                    student=instance.student,
                    is_access=is_access
                )
            )

        if create_student_access_section:
            StudentAccessSection.objects.bulk_create(create_student_access_section)
