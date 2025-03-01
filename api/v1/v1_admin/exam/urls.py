from rest_framework_nested import routers
from rest_framework.urls import path
from django.urls import include

from . import views


app_name = 'admin_exam_api'

router = routers.DefaultRouter()

router.register('exam', views.ExamViewSet, basename='exam')

exam_router = routers.NestedDefaultRouter(router, 'exam', lookup='exam')
exam_router.register("question", views.QuestionViewSet, basename='admin_question')
exam_router.register("score", views.ScoreViewSet, basename='admin_score')

question_router = routers.NestedDefaultRouter(exam_router, "question", lookup='question')
question_router.register("answer", views.AnswerViewSet, basename='admin_answer')

urlpatterns = [
    path("", include(exam_router.urls)),
    path("", include(question_router.urls)),
]
urlpatterns += router.urls
