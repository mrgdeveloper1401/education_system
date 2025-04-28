from celery import shared_task


@shared_task
def send_successfully_signup(phone_number):
    pass
