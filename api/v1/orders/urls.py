from rest_framework import routers

from api.v1.orders.views import CourseSignupViewSet

app_name = "v1_orders"

router = routers.DefaultRouter()

# router.register("orders", OrderViewSet)
router.register("course_signup", CourseSignupViewSet, basename="order_course_signup")
# router.register("user_payment", PaymentViewSet, basename="order_user_payment")

urlpatterns = []
urlpatterns += router.urls
