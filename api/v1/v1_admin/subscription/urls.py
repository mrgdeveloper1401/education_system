from rest_framework import routers

from . import views

app_name = 'admin_subscription_api'

router = routers.DefaultRouter()

router.register("student_enrollment", views.AdminStudentEnrollmentViewSet, basename="student_enrollment")
router.register("teacher_enrollment", views.AdminTeacherEnrollmentViewSet, basename="teacher_enrollment")

urlpatterns = router.urls
