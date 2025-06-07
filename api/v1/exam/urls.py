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

# exam_router.register("score", views.ScoreViewSet, basename='get_student')

# question_router = routers.NestedDefaultRouter(exam_router, "question", lookup="question")
# question_router.register("answer", views.AnswerViewSet, basename='answer')

urlpatterns = [
    path("", include(exam_router.urls)),
    # path("", include(question_router.urls)),
]
urlpatterns += router.urls
