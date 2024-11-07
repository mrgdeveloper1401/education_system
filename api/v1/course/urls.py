from rest_framework.routers import DefaultRouter

from .views import TermViewSet, CourseViewSet, UnitSelectionViewSet

router = DefaultRouter()
router.register('term', TermViewSet, basename='term')
router.register('course', CourseViewSet, basename='course')
router.register('unit_selection', UnitSelectionViewSet, basename='unit_selection')

app_name = 'course'
urlpatterns = []
urlpatterns += router.urls
