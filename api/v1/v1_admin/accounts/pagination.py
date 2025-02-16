from rest_framework import pagination


class BestStudentPagination(pagination.PageNumberPagination):
    page_size = 20
