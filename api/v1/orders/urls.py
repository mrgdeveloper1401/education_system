from rest_framework import routers

from api.v1.orders.views import OrderViewSet, CourseSignupViewSet


app_name = "v1_orders"

router = routers.DefaultRouter()

router.register("orders", OrderViewSet)
router.register("course_signup", CourseSignupViewSet)

urlpatterns = []
urlpatterns += router.urls
