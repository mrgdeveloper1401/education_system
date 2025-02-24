from rest_framework import pagination


class BestStudentPagination(pagination.PageNumberPagination):
    page_size = 20


class ListStudentByIdPagination(pagination.PageNumberPagination):
    page_size = 20
