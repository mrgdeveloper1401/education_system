from rest_framework import routers
from rest_framework.urls import path

from api.v1.orders.views import CourseSignupView

app_name = "v1_orders"

router = routers.DefaultRouter()

# router.register("orders", OrderViewSet)
# router.register("course_signup", CourseSignupViewSet, basename="order_course_signup")
# router.register("user_payment", PaymentViewSet, basename="order_user_payment")

urlpatterns = [
    path("course_signup/", CourseSignupView.as_view(), name="course_signup"),
]
urlpatterns += router.urls
