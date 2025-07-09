from celery import shared_task
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

from accounts.models import User, PrivateNotification
from course.models import Certificate


@shared_task(queue="create_qrcode")
def create_qr_code(*args, **kwargs):
    # get data
    information = kwargs.get("information")
    certificate_id = kwargs["certificate_id"]['id']

    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Add data to QR code
    qr.add_data(str(information))
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Prepare to save the image
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    # Get certificate and save QR code
    certificate = Certificate.objects.filter(id=certificate_id).only("id").first()
    filename = f"qr_code_{certificate.unique_code}.png"

    certificate.qr_code.save(
        filename,
        ContentFile(buffer.getvalue()),
        save=True
    )

    return f"QR code generated for certificate {certificate_id}"


@shared_task(queue="notification")
def admin_user_request_certificate(body, link):
    admin_user = User.objects.filter(
        is_active=True,
        is_staff=True
    ).only(
        "mobile_phone"
    )
    lst = [
        PrivateNotification(
            user=i,
            body=body,
            title = "certificate",
            notification_type="certificate",
            char_link=link
        )
        for i in admin_user
    ]

    if lst:
        PrivateNotification.objects.bulk_create(lst)
