from rest_framework import routers
from rest_framework.urls import path

from api.v1.orders.views import CourseSignupView

app_name = "v1_orders"

router = routers.DefaultRouter()

urlpatterns = [
    path("course_signup/", CourseSignupView.as_view(), name="course_signup"),
]
urlpatterns += router.urls
