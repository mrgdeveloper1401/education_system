from uuid import uuid4

from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from .models import User, Coach, Student, Ticket, PrivateNotification


@receiver(post_save, sender=User)
def create_coach(sender, instance, created, **kwargs):
    instance_number = f"s{str(timezone.now().date().year)[-2:]}{str(uuid4().int)[:8]}"
    if created:
        if not instance.is_superuser:
            if instance.is_coach:
                Coach.objects.get_or_create(user=instance, coach_number=instance_number.replace("s", "c"))
            if instance.is_student:
                Student.objects.get_or_create(user=instance, student_number=instance_number)
    else:
        get_student = Student.objects.filter(user=instance)
        if get_student and instance.is_coach:
            instance.is_coach = False
            instance.save()
            raise ValidationError({"message": "user is student, these user can not set coach"})
        if get_student and instance.is_staff:
            instance.is_staff = False
            instance.save()
            raise ValidationError({"message": "user is student, these user can not set staff"})


@receiver(post_save, sender=Ticket)
def send_notification_when_create_ticket(sender, instance, created, **kwargs):
    if created:
        admin_users = User.objects.filter(is_staff=True, is_active=True).only("is_staff", "mobile_phone", "is_active")
        ticket = [
            PrivateNotification(
                user=i,
                body="یک تیکت جدید ثبت شده هست",
                notification_type="ticket",
                title="create ticket"
            )
            for i in admin_users
        ]

        if ticket:
            PrivateNotification.objects.bulk_create(ticket)
