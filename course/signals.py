from django.db.models.signals import m2m_changed
from django.dispatch import receiver
# from .models import LessonTakenByStudent, LessonTakenByCoach


# @receiver(m2m_changed, sender=LessonTakenByStudent.coach.through)
# def create_lesson_by_coach(sender, instance, action, **kwargs):
#     if action == "post_add":
#         existing_coach = LessonTakenByCoach.objects.filter(
#             coach__in=instance.coach.all(),
#             course=instance.course,
#         )
#         lesson_by_coach = [
#             LessonTakenByCoach(
#                 coach=i,
#                 course=instance.course,
#             )
#             for i in instance.coach.exclude(lesson_provide_coach__in=existing_coach)
#         ]
#         LessonTakenByCoach.objects.bulk_create(lesson_by_coach)
