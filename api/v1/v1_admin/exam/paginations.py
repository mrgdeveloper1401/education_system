from rest_framework import pagination


class ExamPagination(pagination.PageNumberPagination):
    page_size = 20
