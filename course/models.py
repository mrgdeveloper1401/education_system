from django.db import models
from core.models import UpdateMixin, CreateMixin, SoftDeleteMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from treebeard.mp_tree import MP_Node

from course.validators import max_upload_image_validator


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
    course_name = models.CharField(max_length=100, db_index=True)
    course_description = models.TextField()
    course_price = models.FloatField(help_text=_("قیمت دوره که بر اساس تومان میباشد"))
    course_duration = models.CharField(help_text=_("مدت زمان دوره"), max_length=20)
    course_image = models.ImageField(upload_to="course_image/%Y/%m/%d", validators=[max_upload_image_validator],
                                     help_text=_("حداکثر اندازه عکس 1 مگابایت هست"), blank=True)
    is_publish = models.BooleanField(default=True)

    def __str__(self):
        return self.course_name

    class Meta:
        db_table = 'course'
        verbose_name = _("درس")
        verbose_name_plural = _("درس ها")
        ordering = ("-created_at",)


class Section(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='sections')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True,
                                       help_text=_("در دسترس بودن"))
    cover_image = models.ImageField(upload_to="section_cover_image/%Y/%m/%d", null=True,
                                    validators=[max_upload_image_validator])

    class Meta:
        ordering = ('created_at',)
        db_table = 'course_section'
        verbose_name = _("قسمت")
        verbose_name_plural = _("قسمت های دوره")


class SectionVideo(CreateMixin, UpdateMixin, SoftDeleteMixin):
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name='section_videos')
    video = models.FileField(upload_to="section_video/%Y/%m/%d", validators=[FileExtensionValidator(["mp4"])])
    is_publish = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.section_id} {self.is_publish}'

    class Meta:
        db_table = 'course_section_video'


class SectionFile(CreateMixin, UpdateMixin, SoftDeleteMixin):
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name='section_files')
    zip_file = models.FileField(upload_to="section_file/%Y/%m/%d", validators=[FileExtensionValidator(["zip", "rar"])],
                                blank=True)
    is_publish = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.section_id} {self.is_publish}'

    class Meta:
        db_table = "course_section_file"


class StudentEnrollment(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey("accounts.Student", on_delete=models.DO_NOTHING, related_name="student_enrollment")
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name="student_course_enrollment")
    status = models.CharField(choices=[("active", _("فعال")), ("dropped", _("ترک شده"))], max_length=7, default="active")

    class Meta:
        db_table = 'student_enrollment'
        ordering = ['-created_at']


class TeacherEnrollment(CreateMixin, UpdateMixin, SoftDeleteMixin):
    coach = models.ForeignKey("accounts.Coach", on_delete=models.DO_NOTHING, related_name="instructing_courses")
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name="coach_enrollment")
    role = models.CharField(
        choices=[("main", _("استاد اصلی")), ("assistance", _("اساد کمکی"))],
        max_length=10
    )

    class Meta:
        db_table = 'teacher_enrollment'
        ordering = ['-created_at']


class Comment(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey('accounts.User', on_delete=models.DO_NOTHING, related_name='user_comment')
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='comments')
    comment_body = models.TextField(_("متن کامنت"))
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = 'comment'
        verbose_name = _("نظر")
        verbose_name_plural = _("نظرات")
