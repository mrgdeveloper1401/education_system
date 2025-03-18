from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from .models import StudentSectionScore, Section


# @receiver(post_save, sender=StudentSectionScore)
# def unlock_next_section(sender, instance, created,**kwargs):
#     if instance.score >= 60:
#         current_section = instance.section
#         next_section = (Section.objects.filter(course=current_section.course, order__gt=current_section.order).
#                         order_by('order').first())
#
#         if next_section:
#             assign_perm("can_access_section", instance.student, next_section)