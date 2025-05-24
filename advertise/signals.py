from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save

from accounts.models import User, PrivateNotification
from . import models


@receiver(post_save, sender=models.ConsultationRequest)
def create_notification_after_signup_advertise(sender, instance, created, **kwargs):
    if created:
        admin_user = User.objects.filter(is_staff=True).only("is_staff", "mobile_phone")
        create_data = [
            PrivateNotification(
                user=i,
                body="یک نفر درخواست مشاوره رو داده هست",
                notification_type="advertise",
                title="signup advertise",
            )
            for i in admin_user
        ]
        if create_data:
            PrivateNotification.objects.bulk_create(create_data)
