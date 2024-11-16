from rest_framework.pagination import PageNumberPagination


class AdvertisePagination(PageNumberPagination):
    page_size = 5
