from rest_framework import pagination


class TeacherStudentEnrollmentPagination(pagination.PageNumberPagination):
    page_size = 20
