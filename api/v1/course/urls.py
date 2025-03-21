from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

router = routers.DefaultRouter()
router.register("student_lesson_course", views.PurchasesViewSet, basename="student_lesson_course")
router.register('student_send_file', views.StudentSendfileViewSet, basename="student_send_file")

lesson_course_router = routers.NestedDefaultRouter(router, "student_lesson_course",
                                                   lookup="student_lesson_course")


app_name = 'course'
urlpatterns = [
    path("", include(lesson_course_router.urls)),
    path('section_files/', views.StudentSectionFileApiView.as_view(), name='section_files'),
]
urlpatterns += router.urls
