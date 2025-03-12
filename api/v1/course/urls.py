from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

router = routers.DefaultRouter()
router.register("purchase", views.PurchasesViewSet, basename="purchases")

app_name = 'course'
urlpatterns = [
]
urlpatterns += router.urls
