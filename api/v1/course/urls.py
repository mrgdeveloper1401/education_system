from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

router = routers.DefaultRouter()
router.register("student_lesson_course", views.PurchasesViewSet, basename="student_lesson_course")
router.register("coach_lesson_course", views.CoachLessonCourseViewSet, basename="coach_lesson_course")
router.register("student_coach_lesson_course", views.StudentLessonCourseViewSet, basename="student_coach_lesson_course")
router.register("coach_present_absent", views.PresentAbsentViewSet, basename="coach_present_absent")
router.register("poll_answer", views.StudentPollAnswer, basename="student_poll_answer")

lesson_course_router = routers.NestedDefaultRouter(router, "student_lesson_course",
                                                   lookup="student_lesson_course")
lesson_course_router.register("student_list_present_absent", views.StudentListPresentAbsentViewSet,
                              basename="student_list_present_absent")
coach_lesson_course_router = routers.NestedDefaultRouter(router, "coach_lesson_course",
                                                         lookup="coach_lesson_course")
# lesson_course_router.register("student_online_link", views.StudentOnlineLinkViewSet, basename="student_online_link")
coach_lesson_course_router.register("online_link", views.OnlineLinkViewSet, basename="coach_online_link")

app_name = 'course'
urlpatterns = [
    path("", include(lesson_course_router.urls)),
    path("", include(coach_lesson_course_router.urls)),
    path("student_lesson_course/<int:student_lesson_course_pk>/student_online_link/",
         views.StudentOnlineLinkApiView.as_view(), name="student_online_link"),
]
urlpatterns += router.urls
