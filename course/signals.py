from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import PrivateNotification, User
from .enums import SendFileChoices
from .models import StudentAccessSection, SendSectionFile, CallLessonCourse, StudentEnrollment, StudentSectionScore


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
def create_student_section_score(sender, instance, **kwargs):
    if instance.score and instance.score >= 60:
        score = StudentSectionScore.objects.filter(
            student=instance.student,
            section=instance.section_file.section,
        )
        if score:
            score.update(score=instance.score)
        else:
            StudentSectionScore.objects.create(
                student=instance.student,
                section=instance.section_file.section,
                score=instance.score
            )


@receiver(post_save, sender=SendSectionFile)
def send_notification_when_score_is_accepted(sender, instance, **kwargs):
    category_id = instance.section_file.section.course.category_id
    course_id = instance.section_file.section.course_id

    if instance.score:
        PrivateNotification.objects.create(
            user=instance.student.user,
            body="دانش اموز محترم نمره شما ثبت و ویرایش شده هست",
            char_link=f'category_id: {category_id}/send_file_pk: {course_id}'
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
        lesson_course_sections = instance.lesson_course.course.sections.filter(is_publish=True)
        print(lesson_course_sections)
        create_student_access_section = []

        for i in lesson_course_sections:
            if not StudentAccessSection.objects.filter(student=instance.student, section=i).exists():
                create_student_access_section.append(
                    StudentAccessSection(
                        student=instance.student,
                        section=i,
                    )
                )

        if create_student_access_section:
            create_student_access_section[0].is_access = True
            StudentAccessSection.objects.bulk_create(create_student_access_section)
