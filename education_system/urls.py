from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from .base import MEDIA_URL, MEDIA_ROOT, DEBUG

swagger_url = [
    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

simple_jwt_url = [
    path('jwt/create/', TokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),
]

api_url = [
    path('api_auth_user/', include('api.v1.user.urls', namespace='user')),
    path('api_advertise/', include('api.v1.advertise.urls', namespace='advertise')),
    path('api_course/', include('api.v1.course.urls', namespace='course')),
    path('api_discount/', include('api.v1.coupons.urls', namespace='coupons')),
    path('api_subscription/', include('api.v1.subscription.urls', namespace='subscription')),
    path("api_cart/", include('api.v1.cart.urls', namespace='cart')),

]
urlpatterns = [
    path("admin/", admin.site.urls),
]

urlpatterns += swagger_url + api_url + simple_jwt_url

if DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
