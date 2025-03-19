from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

router = routers.DefaultRouter()
router.register("student_lesson_course", views.PurchasesViewSet, basename="student_lesson_course")
router.register("student_access_section", views.StudentAccessSectionViewSet, basename="student_access_section")
router.register("practice", views.PracticeViewSet, basename="practice")

lesson_course_router = routers.NestedDefaultRouter(router, "student_lesson_course",
                                                   lookup="student_lesson_course")
student_access_section_router = routers.NestedDefaultRouter(router, "student_access_section",
                                                            lookup="student_access_section")
student_access_section_router.register("student_present_absent", views.StudentPresentAbsentViewSet,
                                       basename="student_present_absent")
practice_router = routers.NestedDefaultRouter(router, "practice", lookup="practice")
practice_router.register("send_practice", views.StudentSendPracticeViewSet, basename="send_practice")

app_name = 'course'
urlpatterns = [
    path("", include(lesson_course_router.urls)),
    path("", include(student_access_section_router.urls)),
    path("", include(practice_router.urls))
]
urlpatterns += router.urls
