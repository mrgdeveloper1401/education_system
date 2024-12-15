from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

router = routers.DefaultRouter()
router.register('term', views.CategoryViewSet, basename='term')
router.register('lesson_taken_student', views.LessonByStudentTakenViewSet, basename='lesson-taken-student')
router.register("lesson_taken_coach", views.LessonByCoachTakenViewSet, basename='lesson-taken-coach')
router.register('course', views.CourseViewSet, basename='course')

term_router = routers.NestedSimpleRouter(router, r'term', lookup='term')
term_router.register('course', views.CourseViewSet, basename='nested-course')

course_router = routers.NestedSimpleRouter(term_router, r'course', lookup='course')
course_router.register('section', views.SectionViewSet, basename='nested-section')
course_router.register('comment', views.CommentViewSet, basename='nested-comment')
course_router.register('quiz', views.QuizViewSet, basename='nested-quiz')

course_practice = routers.NestedSimpleRouter(router, r'course', lookup='course')
course_practice.register('practice', views.PracticeViewSet, basename='nested-practice')

practice = routers.NestedSimpleRouter(course_practice, r'practice', lookup='practice')
practice.register('submit-practice', views.SubmitPracticeViewSet, basename='nested-submit-practice')

app_name = 'course'
urlpatterns = [
    path('', include(term_router.urls)),
    path('', include(course_router.urls)),
    path('', include(course_practice.urls)),
    path('', include(practice.urls))
]
urlpatterns += router.urls
