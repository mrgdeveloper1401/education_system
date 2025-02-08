from datetime import datetime

from celery import shared_task

from subscription_app.models import Subscription


@shared_task
def subscription_change_status():
    all_subscriptions = Subscription.objects.filter(status="active")
    update_subscription = []
    for subscription in all_subscriptions:
        if subscription.end_date < datetime.now().date():
            subscription.status = "expired"
            update_subscription.append(subscription)
    if update_subscription:
        Subscription.objects.bulk_update(update_subscription, ['status'])
