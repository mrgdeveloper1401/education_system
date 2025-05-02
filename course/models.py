from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import Student
from core.models import UpdateMixin, CreateMixin, SoftDeleteMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from treebeard.mp_tree import MP_Node

from course.enums import ProgresChoices, SectionFileType, StudentStatusChoices, RateChoices, SendFileChoices, \
    CallStatusChoices
from course.utils import student_send_section_file
from course.validators import max_upload_image_validator


class Category(MP_Node, CreateMixin, UpdateMixin, SoftDeleteMixin):
    category_name = models.CharField(max_length=100, db_index=True)
    node_order_by = ["category_name"]
    image = models.ImageField(upload_to="category_images/%Y/%m/%d", null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)

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
    price = models.FloatField(help_text=_("قیمت دوره"), blank=True, null=True)
    is_free = models.BooleanField(default=False)
    facilities = ArrayField(models.CharField(max_length=30), blank=True, null=True)
    course_type = models.CharField(max_length=13, null=True, blank=True)
    time_course = models.CharField(max_length=10, help_text="مدت زمان دوره", blank=True)
    course_age = models.CharField(max_length=30, help_text="بازه سنی دوره", blank=True)

    def __str__(self):
        return self.course_name

    def clean(self):
        if self.price and self.is_free is True:
            raise ValidationError({"is_free": _("course not have is free and price")})
        if not self.price and self.is_free is False:
            raise ValidationError({"is_free": _("you must select one item between (is_free and price)")})

    @property
    def calc_discount_value(self):
        discount = self.discounts.filter(is_active=True)

        if self.price is None:
            return None

        if discount:
            price = (self.price * discount.last().percent) / 100
            return price
        return None

    @property
    def amount_discount(self):
        discount = self.discounts.filter(is_active=True)

        if discount:
            return discount.last().percent
        else:
            return None

    @property
    def final_price(self):
        if self.price is None:
            return None
        return self.price - self.calc_discount_value

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

    @property
    def progress_bar(self):
        accessed_section_count = StudentAccessSection.objects.filter(
            student__in=self.students.all(),
            section__course=self.course,
            is_access=True
        ).count()
        total_section_count = self.course.sections.count()

        if total_section_count == 0:
            return 0

        progress_percentage = (accessed_section_count / total_section_count) * 100
        return round(progress_percentage, 2)

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
    file_type = models.CharField(choices=SectionFileType, max_length=9, null=True)
    answer = models.FileField(upload_to="answer/section_file/%Y/%m/%d",
                              validators=[FileExtensionValidator(["zip", "rar"])],
                              blank=True, null=True)
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
        ordering = ("created_at",)


class PresentAbsent(CreateMixin, UpdateMixin):
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING,
                                related_name="section_present_absent",
                                limit_choices_to={'is_publish': True})
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, related_name="student_present_absent",
                                limit_choices_to={"is_active": True})
    student_status = models.CharField(choices=StudentStatusChoices.choices, default=StudentStatusChoices.nothing)

    class Meta:
        db_table = "course_section_present_absent"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=['section', "student"], name="unique_section_student")
        ]


class StudentSectionScore(CreateMixin, UpdateMixin, SoftDeleteMixin):
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name='section_score',
                                limit_choices_to={"is_publish": True})
    score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, related_name="student_section_score", null=True)

    class Meta:
        db_table = "course_section_score"


class SendSectionFile(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey("accounts.Student", on_delete=models.DO_NOTHING, related_name="send_section_files",
                                limit_choices_to={"is_active": True})
    section_file = models.ForeignKey(SectionFile, on_delete=models.CASCADE, related_name='section_files')
    send_file_status = models.CharField(choices=SendFileChoices.choices, max_length=14,
                                        help_text=_("وضعیت فایل ارسالی"),
                                        default=SendFileChoices.accept_to_wait, null=True, blank=True)
    zip_file = models.FileField(help_text=_("فایل ارسالی"), upload_to=student_send_section_file)
    comment_student = models.TextField(help_text=_("توضیحی در مورد تمرین ارسالی"), null=True)
    comment_teacher = models.CharField(max_length=255, help_text=_("توضیح مربی در مورد فایل ارسال شده دانشجو"),
                                       null=True, blank=True)
    score = models.FloatField(help_text=_("نمره تکلیف ارسالی"), blank=True, null=True,
                              validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        db_table = "send_file"
        ordering = ('-created_at',)

    def save(self, *args, **kwargs):
        if self.score:
            if self.score >= 60:
                self.send_file_status = SendFileChoices.accepted
            else:
                self.send_file_status = SendFileChoices.rejected
        super().save(*args, **kwargs)

# TODO, when clean migration, we remove field null in model Certificate
class Certificate(CreateMixin, UpdateMixin, SoftDeleteMixin):
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name="section_certificates",
                               limit_choices_to={"is_publish": True}, null=True)
    student = models.ForeignKey("accounts.Student", on_delete=models.DO_NOTHING, related_name="student_certificates",
                                limit_choices_to={"is_active": True})

    class Meta:
        db_table = 'course_certificate'


class Comment(MP_Node, CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey('accounts.User', on_delete=models.DO_NOTHING, related_name='user_comment',
                             limit_choices_to={"is_active": True})
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name='category_comments')
    comment_body = models.TextField(_("متن کامنت"))
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = 'comment'
        ordering = ("-created_at",)


class OnlineLink(CreateMixin, UpdateMixin, SoftDeleteMixin):
    class_room = models.ForeignKey(LessonCourse, on_delete=models.DO_NOTHING, related_name="online_link")
    link = models.URLField()
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = "online_link"
        ordering = ("-created_at",)


class Question(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(max_length=255)
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = "poll_question"
        ordering = ("-created_at",)


class SectionQuestion(CreateMixin, UpdateMixin, SoftDeleteMixin):
    question_title = models.CharField(max_length=255, null=True)
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, related_name="section_question",
                                limit_choices_to={"is_publish": True})
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = "section_question"
        ordering = ("-created_at",)


class AnswerQuestion(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey("accounts.Student", on_delete=models.DO_NOTHING, related_name="student_poll_answer",
                                limit_choices_to={"is_active": True})
    section_question = models.ForeignKey(SectionQuestion, on_delete=models.DO_NOTHING, related_name="section_question")
    rate = models.CharField(choices=RateChoices.choices)

    class Meta:
        db_table = "poll_answer"
        ordering = ("created_at",)


class CallLessonCourse(CreateMixin, UpdateMixin, SoftDeleteMixin):
    lesson_course = models.ForeignKey(LessonCourse, on_delete=models.DO_NOTHING, related_name="call")
    call = models.CharField(max_length=50, help_text=_("تماس"))
    status = models.CharField(max_length=13, help_text=_("وضعیت تماس"), choices=CallStatusChoices.choices,
                              db_index=True)
    call_answering = models.CharField(max_length=20, help_text=_("پاسخگوی تماس"))
    project = models.CharField(max_length=30, help_text=_("بابت پروژه"))
    call_date = models.DateField(help_text=_("تاریخ مکالمه"))
    result_call = models.TextField(help_text=_("نتیجه مکالمه"))
    cancellation_alert = models.BooleanField(default=False, help_text=_("هشدار انصراف"))
    student = models.ForeignKey("accounts.Student", on_delete=models.DO_NOTHING, related_name="student_call",
                                null=True)

    def __str__(self):
        return self.call

    class Meta:
        db_table = "call_lesson_course"
        ordering = ("-created_at",)


class SignupCourse(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name="course_signup")
    student_name = models.CharField(max_length=120, help_text="نام و نام خوادگی داشن اموز")
    phone_number = models.CharField(max_length=15, help_text="شماره تلفن ")
    i_have_computer = models.BooleanField(default=True)

    def __str__(self):
        return self.student_name

    class Meta:
        db_table = "course_signup"
