from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from accounts.models import PrivateNotification, User, Student, Invitation
from .enums import SendFileChoices
from .models import StudentAccessSection, SendSectionFile, CallLessonCourse, StudentEnrollment, StudentSectionScore, \
    SignupCourse, LessonCourse


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
    # category_id = instance.section_file.section.course.category_id
    # course_id = instance.section_file.section.course_id
    send_file_pk = instance.id
    section_file_pk = instance.section_file_id
    section_pk = instance.section_file.section_id

    if instance.score:
        PrivateNotification.objects.create(
            user=instance.student.user,
            body="دانش اموز محترم نمره شما ثبت و ویرایش شده هست",
            char_link=f'section_pk:{section_pk}/section_file_pk:{section_file_pk}/send_file_pk:{send_file_pk}',
            notification_type="accept score",
            title="accept score",
        )


@receiver(post_save, sender=CallLessonCourse)
def create_admin_notification_when_cancel_student(sender, instance, created, **kwargs):
    if instance.cancellation_alert:
        admin_user = User.objects.filter(is_staff=True).only("is_staff", "mobile_phone")
        lst = [
            PrivateNotification(
                user=i,
                title='cancel student',
                body="یکی از دانش اموزان در خواست انصرافی رو داده هست",
                notification_type="cancel signup student"
            )
            for i in admin_user
        ]

        if lst:
            PrivateNotification.objects.bulk_create(lst)


@receiver(post_save, sender=StudentEnrollment)
def access_student_access_section(sender, instance, created, **kwargs):
    if created:
        lesson_course_sections = instance.lesson_course.course.sections.filter(is_publish=True)
        # print(lesson_course_sections)
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


@receiver(post_save, sender=SignupCourse)
def create_user_after_signup_course(sender, instance, created, **kwargs):
    if created:
        # get user
        user = User.objects.filter(
            mobile_phone=instance.phone_number
        ).only(
            "mobile_phone"
        )

        if not user:
            # create user
            user = User.objects.create_user(
                mobile_phone=instance.phone_number,
            )

            # get referral code
            referral_code = instance.referral_code
            if referral_code:
                # get student
                student = Student.objects.filter(referral_code=referral_code).only("student_number")

                if student:
                    Invitation.objects.create(
                        from_student=student.first(),
                        to_student=user.student,
                    )


# @receiver(post_save, sender=StudentEnrollment)
# def delete_student_in_lesson_course(sender, **kwargs):
#     print(kwargs) # {'signal': <django.db.models.signals.ModelSignal object at 0x7f733b998d90>, 'instance': <StudentEnrollment: StudentEnrollment object (6)>, 'created': False, 'update_fields': None, 'raw': False, 'using': 'default'}
    # print(sender) # <class 'course.models.StudentEnrollment'>
    # print(kwargs.get("instance"))