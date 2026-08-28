from celery import shared_task

from base.utils.send_sms import send_sms

@shared_task(bind=True, queue='otp', max_retries=2)
def send_otp_sms_task(self, phone, value, template_name, template_id):
    try:
        return send_sms(template_id=template_id, mobile=phone, template_name=template_name, value=value)
    except Exception as e:
        self.retry(exc=e, count_down=10)
