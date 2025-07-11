from rest_framework import routers

from . import views

app_name = "v1_api_core"

router = routers.SimpleRouter()

router.register("site_map", views.SitemapViewSet, basename="sitemap")
router.register("course_site_information", views.CourseSiteInformationViewSet, basename="course-site-information")

urlpatterns = router.urls
