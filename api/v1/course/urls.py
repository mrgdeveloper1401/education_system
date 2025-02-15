from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

router = routers.DefaultRouter()
router.register('category', views.CategoryViewSet, basename='term')
# router.register('lesson_taken_student', views.LessonByStudentTakenViewSet, basename='lesson-taken-student')
# router.register("lesson_taken_coach", views.LessonByCoachTakenViewSet, basename='lesson-taken-coach')
# router.register('course', views.CourseViewSet, basename='course')

category_router = routers.NestedDefaultRouter(router, r'category', lookup='category')
category_router.register('course', views.CourseViewSet, basename='nested-course')

course_router = routers.NestedDefaultRouter(category_router, r'course', lookup='course')
# course_router.register('class_room', views.ClassRoomViewSet, basename='class-room')
course_router.register('section', views.SectionViewSet, basename='nested-section')
course_router.register('comment', views.CommentViewSet, basename='nested-comment')
# course_router.register('quiz', views.QuizViewSet, basename='nested-quiz')

section_router = routers.NestedDefaultRouter(course_router, "section", lookup="section")
section_router.register("section_video", views.SectionVideoViewSet, basename="section_video")
section_router.register("section_file", views.SectionFileViewSet, basename="section_file")
section_router.register("section_image", views.SectionImagesViewSet, basename="section_image")
# course_practice = routers.NestedSimpleRouter(router, r'course', lookup='course')
# course_practice.register('practice', views.PracticeViewSet, basename='nested-practice')
#
# practice = routers.NestedSimpleRouter(course_practice, r'practice', lookup='practice')
# practice.register('submit-practice', views.SubmitPracticeViewSet, basename='nested-submit-practice')

# quiz = routers.NestedSimpleRouter(course_router, r'quiz', lookup='quiz')
# quiz.register('question', views.QuestionViewSet, basename='nested-question')

app_name = 'course'
urlpatterns = [
    path('', include(category_router.urls)),
    path('', include(course_router.urls)),
    path("", include(section_router.urls)),
    # path('', include(course_practice.urls)),
    # path('', include(practice.urls)),
    # path('', include(quiz.urls)),
]
urlpatterns += router.urls
