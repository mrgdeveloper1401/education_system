from rest_framework.pagination import PageNumberPagination


class AdminPagination(PageNumberPagination):
    page_size = 20
