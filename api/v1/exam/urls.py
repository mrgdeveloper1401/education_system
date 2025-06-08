from rest_framework_nested import routers
from rest_framework.urls import path
from django.urls import include

from . import views

app_name = "api_exam"

router = routers.DefaultRouter()

router.register(r'exam', views.ExamViewSet, basename='exam')

exam_router = routers.NestedDefaultRouter(router, "exam", lookup="exam")
exam_router.register("questions", views.QuestionViewSet, basename='question')
exam_router.register('participation', views.ParticipationViewSet, basename='participation')

participation_router = routers.NestedSimpleRouter(exam_router, r"participation", lookup="participation")
participation_router.register("answer", views.AnswerViewSet, basename='answer')

urlpatterns = [
    path("", include(exam_router.urls)),
    path("", include(participation_router.urls)),
    path('answers/<int:pk>/score/', views.CoachScoreAnswerView.as_view(), name='coach-score-answer'),
]
urlpatterns += router.urls
