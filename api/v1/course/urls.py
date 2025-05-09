from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

router = routers.DefaultRouter()
router.register("student_lesson_course", views.PurchasesViewSet, basename="student_lesson_course")
router.register("coach_lesson_course", views.CoachLessonCourseViewSet, basename="coach_lesson_course")
router.register("student_coach_lesson_course", views.StudentLessonCourseViewSet, basename="student_coach_lesson_course")
router.register("poll_answer", views.StudentPollAnswer, basename="student_poll_answer")
router.register("home_category", views.HomeCategoryViewSet, basename="home_category")

lesson_course_router = routers.NestedDefaultRouter(router, "student_lesson_course",
                                                   lookup="student_lesson_course")
coach_lesson_course = routers.NestedDefaultRouter(router, "coach_lesson_course",
                                                  lookup="coach_lesson_course")
coach_lesson_course.register("call_lesson_course", views.CallLessonCourseViewSet, basename="call_lesson_course")
coach_lesson_course.register("coach_comment", views.CommentViewSet, basename="coach_comment")
lesson_course_router.register("student_comment", views.CommentViewSet, basename="comment")
lesson_course_router.register("student_list_present_absent", views.StudentListPresentAbsentViewSet,
                              basename="student_list_present_absent")
coach_lesson_course_router = routers.NestedDefaultRouter(router, "coach_lesson_course",
                                                         lookup="coach_lesson_course")
coach_lesson_course_router.register("online_link", views.OnlineLinkViewSet, basename="coach_online_link")

home_category_router = routers.NestedSimpleRouter(router, "home_category", lookup="home_category")
home_category_router.register("home_course", views.HomeCourseViewSet, basename="home_course")

app_name = 'course'
urlpatterns = [
    path("", include(lesson_course_router.urls)),
    path("", include(coach_lesson_course_router.urls)),
    path("", include(coach_lesson_course.urls)),
    path("", include(home_category_router.urls)),
    path("student_lesson_course/<int:student_lesson_course_pk>/student_online_link/",
         views.StudentOnlineLinkApiView.as_view(), name="student_online_link"),
]
urlpatterns += router.urls
