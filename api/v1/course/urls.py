from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

router = routers.DefaultRouter()
router.register("lesson_course", views.PurchasesViewSet, basename="purchases")

lesson_course_router = routers.NestedDefaultRouter(router, "lesson_course", lookup="lesson_course")
lesson_course_router.register("present_absent", views.LessonCoursePresentAbsent, basename="present_absent")

app_name = 'course'
urlpatterns = [
    path("", include(lesson_course_router.urls)),
]
urlpatterns += router.urls
