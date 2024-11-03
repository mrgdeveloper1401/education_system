"""
URL configuration for education_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from decouple import config

from .settings import MEDIA_URL, MEDIA_ROOT

debug_mode = config('DEBUG', cast=str)

swagger_url = [
    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

api_url = [
    path('auth_user/', include('api.v1.user.urls', namespace='user')),
    path('advertise/', include('api.v1.advertise.urls', namespace='advertise'))

]
urlpatterns = [
    path("admin/", admin.site.urls),
]

urlpatterns += swagger_url + api_url

if debug_mode:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
