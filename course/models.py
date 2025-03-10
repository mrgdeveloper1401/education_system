from django.db import models
from core.models import UpdateMixin, CreateMixin, SoftDeleteMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from treebeard.mp_tree import MP_Node
from django.utils import timezone

from course.enums import ProgresChoices
# from guardian.shortcuts import assign_perm

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
        # permissions = [
        #     ("can_view_course", "Can View Course")
        # ]


class LessonCourse(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name="lesson_course")
    class_name = models.CharField(help_text=_("نام کلاس"))
    coach = models.ForeignKey("accounts.Coach", on_delete=models.DO_NOTHING, related_name="coach_less_course")
    students = models.ManyToManyField("accounts.Student", related_name="student_lesson_course")
    is_active = models.BooleanField(default=True, help_text=_("دیتا در سطح اپلیکیشن نمایش داده شود یا خیر"))
    progress = models.CharField(help_text=_("وضعیت پیشرفت دوره"), choices=ProgresChoices, max_length=11,
                                default=ProgresChoices.not_started, null=True)

    def __str__(self):
        return self.class_name

    class Meta:
        db_table = 'lesson_course'
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
        # permissions = [
        #     ("can_view_section", "Can View Section")
        # ]


class SectionVideo(CreateMixin, UpdateMixin, SoftDeleteMixin):
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name='section_videos')
    video = models.FileField(upload_to="section_video/%Y/%m/%d", validators=[FileExtensionValidator(["mp4"])])
    is_publish = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.section_id} {self.is_publish}'

    class Meta:
        db_table = 'course_section_video'
        # permissions = [
        #     ("can_view_section_video", "Can View Section Video")
        # ]


class SectionFile(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(help_text=_("عنوان"), max_length=100, null=True)
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name='section_files')
    zip_file = models.FileField(upload_to="section_file/%Y/%m/%d", validators=[FileExtensionValidator(["zip", "rar"])],
                                blank=True)
    is_publish = models.BooleanField(default=True)
    expired_data = models.DateTimeField(null=True, help_text=_("زمان انتقضای تمرین"))
    is_close = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.section_id} {self.is_publish}'

    def save(self, *args, **kwargs):
        if self.expired_data < timezone.now():
            self.is_close = True
        else:
            self.is_close = False
        super().save(*args, **kwargs)

    class Meta:
        db_table = "course_section_file"
        # permissions = [
        #     ("can_view_section_file", "Can View Section File")
        # ]


class SendSectionFile(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey("accounts.Student", on_delete=models.DO_NOTHING, related_name="send_section_files")
    section_file = models.ForeignKey(SectionFile, on_delete=models.DO_NOTHING, related_name='section_files',
                                     validators=[FileExtensionValidator(["rar", "zip"])])
    zip_file = models.FileField(help_text=_("فایل ارسالی"))

    class Meta:
        db_table = "send_file"
        ordering = ('-created_at',)
        # permissions = [
        #     ("can_view_send_section_file", "Can View Send Section File"),
        #     ("can_add_section_file", "Can Add Section File"),
        #     ("can_delete_section_file", "Can Delete Section File"),
        #     ("can_change_section_file", "Can Change Section File"),
        # ]


class Certificate(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name="course_certificates")
    student = models.ForeignKey("accounts.Student", on_delete=models.DO_NOTHING, related_name="student_certificates")
    is_active = models.BooleanField(default=True)
    pdf_file = models.FileField(validators=[FileExtensionValidator(".pdf", )])

    class Meta:
        db_table = 'course_certificate'


class StudentAccessCourse(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey("accounts.Student", on_delete=models.DO_NOTHING,
                                related_name="student_access_course")
    course = models.ForeignKey(Course, related_name="std_course_access_course", on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'student_access_course'
        ordering = ('-created_at',)


class CoachAccessCourse(CreateMixin, UpdateMixin, SoftDeleteMixin):
    coach = models.ForeignKey("accounts.Coach", related_name="coach_access_course", on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, related_name="co_course_access_course", on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'coach_access_course'
        ordering = ('-created_at',)


class Comment(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey('accounts.User', on_delete=models.DO_NOTHING, related_name='user_comment')
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='comments')
    comment_body = models.TextField(_("متن کامنت"))
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = 'comment'
        verbose_name = _("نظر")
        verbose_name_plural = _("نظرات")
