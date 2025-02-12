from rest_framework import routers

from . import views


app_name = 'admin_account'

router = routers.DefaultRouter()

# router.register("ticket_reply", views.TicketReplyViewSet, basename="ticket_reply")

urlpatterns = router.urls
