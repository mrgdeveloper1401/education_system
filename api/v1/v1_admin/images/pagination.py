from rest_framework import pagination


class AdminImagePagination(pagination.PageNumberPagination):
    page_size = 20
