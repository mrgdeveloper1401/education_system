from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    page_size = 5


class CityPagination(PageNumberPagination):
    page_size = 100
