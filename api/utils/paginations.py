from rest_framework.pagination import PageNumberPagination


class FiftyPageNumberPagination(PageNumberPagination):
    page_size = 50
