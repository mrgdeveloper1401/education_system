from django.db import models
from core.models import UpdateMixin, CreateMixin, SoftDeleteMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from treebeard.mp_tree import MP_Node
from rest_framework.validators import ValidationError

from course.validators import max_upload_image_validator
from utils.file_name import section_name, section_filename


class Category(MP_Node, CreateMixin, UpdateMixin, SoftDeleteMixin):
    category_name = models.CharField(max_length=100, db_index=True)
    node_order_by = ["category_name"]

    def __str__(self):
        return self.category_name

    @property
    def sub_category_name(self):
        return self.get_children().values("id", "category_name")

    class Meta:
        db_table = 'category'
        verbose_name = _("ترم")
        verbose_name_plural = _("ترم ها")


class Course(CreateMixin, UpdateMixin, SoftDeleteMixin):
    category = models.ForeignKey(Category, related_name="course_category", on_delete=models.DO_NOTHING)
    course_name = models.CharField(max_length=100)
    course_description = models.TextField()
    course_price = models.FloatField(help_text=_("قیمت دوره که بر اساس تومان میباشد"))
    course_duration = models.CharField(help_text=_("مدت زمان دوره"), max_length=20)
    # course_image = models.ForeignKey("images.Image", on_delete=models.DO_NOTHING, related_name="course_image",
    #                                  blank=True, null=True)
    course_image = models.ImageField(upload_to="course_image/%Y/%m/%d", validators=[max_upload_image_validator])

    def __str__(self):
        return self.course_name

    class Meta:
        db_table = 'course'
        verbose_name = _("درس")
        verbose_name_plural = _("درس ها")
        ordering = ("-created_at",)


class Section(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='sections')
    video = models.FileField(upload_to=section_name, blank=True,
                             validators=[FileExtensionValidator(["mp4"])])
    pdf_file = models.FileField(upload_to=section_filename, validators=[FileExtensionValidator(["pdf"])], blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True,
                                       help_text=_("در دسترس بودن"))
    section_image = models.ForeignKey("images.Image", related_name="section_images", on_delete=models.DO_NOTHING,
                                      blank=True, null=True)

    # def clean(self):
    #     if not self.video and not self.pdf_file:
    #         raise ValidationError({"detail": _("field video or pdf must be set")})

    class Meta:
        ordering = ('created_at',)
        db_table = 'course_section'
        verbose_name = _("قسمت")
        verbose_name_plural = _("قسمت های دوره")


# class SectionImage(CreateMixin, UpdateMixin, SoftDeleteMixin):
#     section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name='section_image')
#     image = models.ForeignKey("images.Image", on_delete=models.DO_NOTHING, related_name="image_section_image")
#     is_active = models.BooleanField(db_default=True)
#
#     class Meta:
#         db_table = 'course_section_image'


class StudentEnrollment(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey("accounts.User", on_delete=models.DO_NOTHING, related_name="student_enrollment")
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name="student_course_enrollment")
    status = models.CharField(choices=[("active", _("فعال")), ("droped", _("ترک شده"))], max_length=6, default="active")

    class Meta:
        unique_together = (("student", "course"),)
        db_table = 'student_enrollment'


class TeacherEnrollment(CreateMixin, UpdateMixin, SoftDeleteMixin):
    instructor = models.ForeignKey("accounts.User", on_delete=models.DO_NOTHING, related_name="instructing_courses")
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name="instructors")
    role = models.CharField(
        choices=[("main", _("استاد اصلی")), ("assistance", _("اساد کمکی"))],
        max_length=10
    )

    class Meta:
        unique_together = (("instructor", "course"),)
        db_table = 'teacher_enrollment'


class Comment(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey('accounts.User', on_delete=models.DO_NOTHING, related_name='user_comment')
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='comments')
    comment_body = models.TextField(_("متن کامنت"))
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = 'comment'
        verbose_name = _("نظر")
        verbose_name_plural = _("نظرات")
