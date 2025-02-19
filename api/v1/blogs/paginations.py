from rest_framework import pagination


class BlogPostPagination(pagination.PageNumberPagination):
    page_size = 20
