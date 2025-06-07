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


urlpatterns = [
    path("", include(exam_router.urls)),
]
urlpatterns += router.urls
