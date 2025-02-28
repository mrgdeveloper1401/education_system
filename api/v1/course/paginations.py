from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination


# class CoursePagination(LimitOffsetPagination):
#     default_limit = 10
#     max_limit = 50


# class CoursePagination(CursorPagination):
#     page_size = 15
#     ordering = '-created_at'


class CourseCategoryPagination(PageNumberPagination):
    page_size = 20


class CoachCoursePagination(PageNumberPagination):
    page_size = 20
