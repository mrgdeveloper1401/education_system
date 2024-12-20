from rest_framework.pagination import PageNumberPagination


class AdvertisePagination(PageNumberPagination):
    page_size = 5


class AnswerPagination(PageNumberPagination):
    page_size = 5


class SlotPagination(PageNumberPagination):
    page_size = 20


class StudentCoachPagination(PageNumberPagination):
    page_size = 5
