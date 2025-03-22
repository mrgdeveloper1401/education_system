from django.db import models

from accounts.models import Student
from core.models import UpdateMixin, CreateMixin, SoftDeleteMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from treebeard.mp_tree import MP_Node

from course.enums import ProgresChoices
from course.utils import student_send_section_file
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


class Course(CreateMixin, UpdateMixin, SoftDeleteMixin):
    category = models.ForeignKey(Category, related_name="course_category", on_delete=models.DO_NOTHING)
    course_name = models.CharField(max_length=100, db_index=True)
    course_description = models.TextField()
    course_image = models.ImageField(upload_to="course_image/%Y/%m/%d", validators=[max_upload_image_validator],
                                     help_text=_("حداکثر اندازه عکس 1 مگابایت هست"), blank=True)
    is_publish = models.BooleanField(default=True)
    project_counter = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        return self.course_name

    class Meta:
        db_table = 'course'
        ordering = ("-created_at",)


class LessonCourse(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name="lesson_course")
    class_name = models.CharField(help_text=_("نام کلاس"))
    coach = models.ForeignKey("accounts.Coach", on_delete=models.DO_NOTHING, related_name="coach_less_course")
    students = models.ManyToManyField("accounts.Student", related_name="student_lesson_course",
                                      limit_choices_to={"is_active": True})
    is_active = models.BooleanField(default=True, help_text=_("دیتا در سطح اپلیکیشن نمایش داده شود یا خیر"))
    progress = models.CharField(help_text=_("وضعیت پیشرفت کلاس"), choices=ProgresChoices, max_length=11,
                                default=ProgresChoices.not_started, null=True)

    def __str__(self):
        return self.class_name

    class Meta:
        db_table = 'lesson_course'
        ordering = ("-created_at",)


class Section(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='sections',
                               limit_choices_to={"is_publish": True})
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to="section_cover_image/%Y/%m/%d", null=True,
                                    validators=[max_upload_image_validator])
    is_publish = models.BooleanField(default=True)

    class Meta:
        ordering = ('created_at',)
        db_table = 'course_section'
        permissions = [
            ("can_access_section", "can access section")
        ]


class SectionVideo(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(max_length=50, help_text=_("عنوان"), null=True)
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name='section_videos',
                                limit_choices_to={"is_publish": True})
    video = models.FileField(upload_to="section_video/%Y/%m/%d", validators=[FileExtensionValidator(["mp4"])])
    is_publish = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.section_id} {self.is_publish}'

    class Meta:
        db_table = 'course_section_video'


class SectionFile(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(help_text=_("عنوان"), max_length=100, null=True)
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name='section_files',
                                limit_choices_to={"is_publish": True})
    zip_file = models.FileField(upload_to="section_file/%Y/%m/%d", validators=[FileExtensionValidator(["zip", "rar"])],
                                blank=True)
    # answer = models.FileField(help_text=_("جواب تمرینات"), null=True, blank=True)
    is_publish = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.section_id} {self.is_publish}'

    class Meta:
        db_table = "course_section_file"


class StudentAccessSection(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, related_name="student_access_section",
                                limit_choices_to={"is_active": True})
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name="student_section",
                                limit_choices_to={"is_publish": True})
    is_access = models.BooleanField(default=False)

    class Meta:
        db_table = "student_access_section"
        ordering = ("-created_at",)


class PresentAbsent(CreateMixin, UpdateMixin, SoftDeleteMixin):
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING,
                                related_name="section_present_absent",
                                limit_choices_to={'is_publish': True})
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, related_name="student_present_absent",
                                limit_choices_to={"is_active": True})
    is_present = models.BooleanField(default=False)

    class Meta:
        db_table = "course_section_present_absent"
        ordering = ("-created_at",)


class StudentSectionScore(CreateMixin, UpdateMixin, SoftDeleteMixin):
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name='section_score',
                                limit_choices_to={"is_publish": True})
    score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, related_name="student_section_score", null=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table = "course_section_score"

    def save(self, *args, **kwargs):
        if self.score >= 60:
            self.is_completed = True
        super().save(*args, **kwargs)


class SendSectionFile(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey("accounts.Student", on_delete=models.DO_NOTHING, related_name="send_section_files",
                                limit_choices_to={"is_active": True})
    section_file = models.ForeignKey(SectionFile, on_delete=models.DO_NOTHING, related_name='section_files')
    zip_file = models.FileField(help_text=_("فایل ارسالی"), upload_to=student_send_section_file)
    description = models.TextField(help_text=_("توضیحی در مورد تمرین ارسالی"), null=True)
    score = models.FloatField(help_text=_("نمره تکلیف ارسالی"), blank=True, null=True,
                              validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        db_table = "send_file"
        ordering = ('-created_at',)


class Certificate(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name="course_certificates",
                               limit_choices_to={"is_publish": True})
    student = models.ForeignKey("accounts.Student", on_delete=models.DO_NOTHING, related_name="student_certificates",
                                limit_choices_to={"is_active": True})
    is_active = models.BooleanField(default=True)
    pdf_file = models.FileField(validators=[FileExtensionValidator(("rar", "zip"))])

    class Meta:
        db_table = 'course_certificate'


class Comment(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey('accounts.User', on_delete=models.DO_NOTHING, related_name='user_comment')
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='comments')
    comment_body = models.TextField(_("متن کامنت"))
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = 'comment'


class OnlineLink(CreateMixin, UpdateMixin, SoftDeleteMixin):
    class_room = models.ForeignKey(LessonCourse, on_delete=models.DO_NOTHING, related_name="online_link")
    link = models.URLField()
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = "online_link"
