from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views
from ...course.views import CrudCourseTypeViewSet

app_name = 'admin_category'

router = routers.DefaultRouter()

router.register('category', views.CategoryViewSet, basename='admin_category')
router.register("present_absent", views.AdminStudentPresentAbsentViewSet, basename='admin_present_absent')
router.register("course_sign_up", views.SignUpCourseViewSet, basename="course_sign_up")
# router.register("student_list_certificate", views.AdminCertificateStudentListView, basename="std_certificate_list")

category_router = routers.NestedSimpleRouter(router, r'category', lookup='category')
category_router.register("course", views.AdminCourseViewSet, basename='admin_course')
category_router.register("admin_comment", views.AdminCommentViewSet, basename='admin_comment')

course_router = routers.NestedDefaultRouter(category_router, r'course', lookup='course')
course_router.register("course_section", views.AdminCourseSectionViewSet, basename='admin_course_section')
course_router.register("class_room", views.AdminLessonCourseViewSet, basename='admin_class_room')
course_router.register("crud_course_type", CrudCourseTypeViewSet, basename="admin_crud_course_type")

section_router = routers.NestedDefaultRouter(course_router, r'course_section', lookup='section')
section_router.register('section_file', views.AdminSectionFileViewSet, basename='admin_section_file')
section_router.register("section_video", views.AdminSectionVideoViewSet, basename='admin_section_video')
section_router.register("section_question", views.AdminSectionQuestionViewSet, basename='admin_section_question')
section_router.register("certificate", views.AdminCertificateViewSet, basename="admin_certificate")

section_question_router = routers.NestedDefaultRouter(section_router, r'section_question', lookup='section_question')
section_question_router.register("poll_answer", views.AdminAnswerQuestionViewSet, basename='admin_poll_answer')

class_room_router = routers.NestedDefaultRouter(course_router, r'class_room', lookup='class_room')
class_room_router.register("student_enrollment", views.StudentEnrollmentView, basename='admin_student_enrollment')

urlpatterns = [
    path("", include(category_router.urls)),
    path('', include(course_router.urls)),
    path("", include(section_router.urls)),
    path("", include(section_question_router.urls)),
    path("", include(class_room_router.urls)),
    # path('course_list/', views.AdminCourseListApiView.as_view(), name='course_list'),
    path("sync_student_access_section/", views.SyncStudentAccessSectionView.as_view(), name='sync_std_section')
]
urlpatterns += router.urls
