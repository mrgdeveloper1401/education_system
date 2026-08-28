from celery import shared_task

from base.utils.send_sms import send_sms


@shared_task(bind=True, queue="advertise", max_retries=2)
def send_sms_accept_advertise_task(self, phone, advertise_date):
    try:
        return send_sms(template_id=741892, mobile=phone, template_name='advertise', value=advertise_date)
    except Exception as e:
        self.retry(exc=e, countdown=10)
