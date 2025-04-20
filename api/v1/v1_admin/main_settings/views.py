from django.db.models import Q
from rest_framework import viewsets, permissions

from main_settings.models import Banner, HeaderSite
from . import serializers
from ...course.paginations import CommonPagination


class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.defer("is_deleted", "deleted_at")
    serializer_class = serializers.BannerSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        if not self.request.method in permissions.SAFE_METHODS:
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()

    def filter_queryset(self, queryset):
        user = self.request.user

        if not self.request.user.is_authenticated:
            return queryset.filter(banner_type__exact='public')
        if user.is_staff is False and user.is_coach:
            return queryset.filter(Q(banner_type__exact="coach") | Q(banner_type__exact='public'))
        if user.is_coach is False and user.is_staff is False:
            return queryset.filter(Q(banner_type__exact="student") | Q(banner_type__exact='public'))
        else:
            return queryset


class HeaderSiteViewSet(viewsets.ModelViewSet):
    queryset = HeaderSite.objects.defer("is_deleted", "deleted_at")
    serializer_class = serializers.HeaderSiteSerializer

    def get_permissions(self):
        if self.request.method in ['POST', "PUT", 'PATCH', 'DELETE']:
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()

    def filter_queryset(self, queryset):
        if self.request.user.is_staff is False:
            return queryset.filter(is_publish=True)
        return super().filter_queryset(queryset)
