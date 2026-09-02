import io
from pathlib import Path
from uuid import uuid4

from PIL.ImageOps import exif_transpose
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from treebeard.mp_tree import MP_Node
from PIL import Image as PILImage

from apps.account_app.models import Student, Coach, User
from apps.core_app.models import UpdateMixin, CreateMixin, SoftDeleteMixin

from apps.course_app.enums import (
    ProgresChoices,
    SectionFileType,
    RateChoices,
    SendFileChoices,
    CallStatusChoices,
    CourseType,
    PlanTypeEnum,
    StudentStatusEnum
)

from apps.course_app.validators import max_upload_image_validator
from apps.discount_app.models import Discount


def student_send_section_file(instance, filename):
    student_number = instance.student.student_number
    created = instance.created_at
    return f"{student_number}_{created}"


class StudentStatusChoices(models.TextChoices):
    present = "present", _("حاضر")
    activity = "activity", _("حضور فعال")
    absent = "absent", _("غایب")
    late_attendance = "late_attendance", _("حضور با تاخیر")
    inactivity = "inactivity", _("عدم فعالیت")
    nothing = "nothing", _("خالی")


class Category(MP_Node, CreateMixin, UpdateMixin, SoftDeleteMixin):
    category_name = models.CharField(max_length=100, db_index=True)
    node_order_by = ("category_name",)
    image = models.ImageField(upload_to="category_images/%Y/%m/%d", null=True, blank=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    description_slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    is_publish = models.BooleanField(default=True)

    @property
    def sub_category_name(self):
        return self.get_children().values("id", "category_name")

    @property
    def _is_webp(self) -> bool:
        return Path(self.image.name).suffix.lower() == ".webp"

    def conv_img_into_webp(self, quality: int = 100):
        if not self.image or self._is_webp:
            return

        buffer = io.BytesIO()
        with PILImage.open(self.image) as img:
            if getattr(img, "is_animated", False):
                # گیف متحرک: باید همه فریم‌ها ذخیره بشن
                img.save(buffer, format="WEBP", quality=quality, save_all=True)
            else:
                img = exif_transpose(img)
                # حفظ کانال آلفا برای png و مشابهش
                mode = "RGBA" if img.mode in ("RGBA", "LA", "P") else "RGB"
                img.convert(mode).save(buffer, format="WEBP", quality=quality)
        new_name = f"{Path(self.image.name).stem}.webp"
        self.image.save(new_name, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        image_changed = True
        if self.pk:
            old = Category.objects.filter(pk=self.pk).only("image").first()
            image_changed = old is None or old.image.name != self.image.name

        if image_changed:
            self.conv_img_into_webp()

        return super().save(*args, **kwargs)

    class Meta:
        db_table = 'category'


class Course(CreateMixin, UpdateMixin, SoftDeleteMixin):
    category = models.ForeignKey(Category, related_name="course_category", on_delete=models.CASCADE)
    course_name = models.CharField(max_length=100)
    course_description = models.TextField()
    description_slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    course_image = models.ImageField(upload_to="course_image/%Y/%m/%d", validators=[max_upload_image_validator],
                                     help_text=_("حداکثر اندازه عکس 1 مگابایت هست"), blank=True)
    is_publish = models.BooleanField(default=True)
    project_counter = models.PositiveSmallIntegerField(null=True)
    # price = models.FloatField(help_text=_("قیمت دوره"), blank=True, null=True)
    is_free = models.BooleanField(default=False)
    facilities = ArrayField(models.CharField(max_length=30), blank=True, null=True)
    course_level = models.CharField(max_length=13, null=True, blank=True)
    time_course = models.CharField(max_length=10, help_text="مدت زمان دوره", blank=True)
    course_age = models.CharField(max_length=30, help_text="بازه سنی دوره", blank=True)
    order_number = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'course'
        constraints = (
            models.UniqueConstraint(fields=("id", "order_number"), name="unique_order_per_course_id"),
        )


class CourseTypeModel(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_type_model")
    price = models.FloatField()
    description = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    course_type = models.CharField(
        choices=CourseType.choices,
        max_length=8,
        default=CourseType.private,
    )
    amount = models.PositiveSmallIntegerField(blank=True)
    plan_type = models.CharField(choices=PlanTypeEnum.choices, max_length=5, blank=True)

    @property
    def have_discount(self):
        content_type = ContentType.objects.get_for_model(self)
        res = Discount.objects.filter(
            content_type=content_type,
            object_id=self.id,
            start_date__lte=timezone.now(),
            end_date__gt=timezone.now(),
            is_active=True
        ).only("percent").last()
        return res

    @property
    def final_price(self):
        price = self.price

        if self.have_discount:
            discount = (self.have_discount.percent * price) / 100
            price = price - discount
        return price

    class Meta:
        db_table = "course_type"


class LessonCourse(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lesson_course")
    class_name = models.CharField(help_text=_("نام کلاس"))
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name="coach_less_course")
    students = models.ManyToManyField(Student, related_name="student_lesson_course",
                                      through="StudentEnrollment")
    is_active = models.BooleanField(default=True, help_text=_("دیتا در سطح اپلیکیشن نمایش داده شود یا خیر"))
    progress = models.CharField(help_text=_("وضعیت پیشرفت کلاس"), choices=ProgresChoices, max_length=11,
                                default=ProgresChoices.not_started, null=True)
    for_mobile = models.BooleanField(default=False)

    class Meta:
        ordering = ("id",)
        db_table = 'lesson_course'


class StudentEnrollment(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_enrollment")
    lesson_course = models.ForeignKey(LessonCourse, on_delete=models.CASCADE,
                                      related_name="lesson_course_enrollment")
    student_status = models.CharField(choices=StudentStatusEnum.choices, max_length=8, default=StudentStatusEnum.active,
                                      blank=True)

    def save(self, *args, **kwargs):
        # print(self.pk)
        # check student dont add in same class
        if self.pk is None and StudentEnrollment.objects.filter(
            student=self.student,
            lesson_course=self.lesson_course,
        ).only("id").exists():
            raise exceptions.ValidationError({"student": "obj already exists"})
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "lesson_course_students"
        # unique_together = ("student", "lesson_course")


class Section(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to="section_cover_image/%Y/%m/%d", null=True,
                                    validators=[max_upload_image_validator])
    is_publish = models.BooleanField(default=True)
    is_last_section = models.BooleanField(default=False,
                                    help_text=_("اگر تیک این مورد خورده باشد یعنی اخرین سکشن برای درس خواهد بود"))

    class Meta:
        db_table = 'course_section'
        permissions = [
            ("can_access_section", "can access section")
        ]


class SectionVideo(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(max_length=50, help_text=_("عنوان"), null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='section_videos')
    video = models.FileField(upload_to="section_video/%Y/%m/%d", validators=[FileExtensionValidator(["mp4"])], blank=True)
    video_url = models.CharField(max_length=500, blank=True, null=True)
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = 'course_section_video'


class SectionFile(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(help_text=_("عنوان"), max_length=100, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='section_files')
    zip_file = models.FileField(upload_to="section_file/%Y/%m/%d", validators=[FileExtensionValidator(["zip", "rar"])],
                                blank=True)
    file_type = models.CharField(choices=SectionFileType, max_length=9, null=True)
    answer = models.FileField(upload_to="answer/section_file/%Y/%m/%d",
                              validators=[FileExtensionValidator(["zip", "rar"])],
                              blank=True, null=True)
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = "course_section_file"


class StudentAccessSection(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_access_section",
                                limit_choices_to={"is_active": True})
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="student_section",
                                limit_choices_to={"is_publish": True})
    is_access = models.BooleanField(default=False)

    class Meta:
        db_table = "student_access_section"


class PresentAbsent(CreateMixin, UpdateMixin):
    section = models.ForeignKey(Section, on_delete=models.CASCADE,
                                related_name="section_present_absent",
                                limit_choices_to={'is_publish': True})
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_present_absent",
                                limit_choices_to={"is_active": True})
    student_status = models.CharField(choices=StudentStatusChoices.choices, default=StudentStatusChoices.nothing)

    class Meta:
        db_table = "course_section_present_absent"
        constraints = [
            models.UniqueConstraint(fields=['section', "student"], name="unique_section_student")
        ]


class StudentSectionScore(CreateMixin, UpdateMixin, SoftDeleteMixin):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='section_score')
    score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_section_score", null=True)

    class Meta:
        db_table = "course_section_score"


class SendSectionFile(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="send_section_files")
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

    def save(self, *args, **kwargs):
        if self.score:
            if self.score >= 60:
                self.send_file_status = SendFileChoices.accepted
            else:
                self.send_file_status = SendFileChoices.rejected
        super().save(*args, **kwargs)


class CertificateTemplate(CreateMixin, UpdateMixin, SoftDeleteMixin):
    template_image = models.ImageField(
        upload_to="certificate_template/%Y/%m/%d",
        validators=(max_upload_image_validator,),
        help_text=_("حداکثر اندازه سایز تمپلیت ۲ مگابایت باشد")
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'certificate_template'


class Certificate(CreateMixin, UpdateMixin, SoftDeleteMixin):
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="section_certificates"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="student_certificates"
    )
    unique_code = models.CharField(
        max_length=36,
        unique=True,
        blank=True,
        null=True
    )
    qr_code = models.ImageField(
        upload_to="certificates/qr_codes/%Y/%m/%d/",
        blank=True
    )
    final_pdf = models.FileField(
        upload_to="certificates/pdf/%Y/%m/%d/",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "certificate"
        # unique_together = ("section", "student")

    def save(self, *args, **kwargs):
        if self.unique_code is None and self.pk is None:
            self.unique_code = str(uuid4())
        super().save(*args, **kwargs)


class Comment(MP_Node, CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_comments')
    comment_body = models.TextField(_("متن کامنت"))
    is_publish = models.BooleanField(default=True)
    is_pined = models.BooleanField(default=False)

    class Meta:
        db_table = 'comment'


class OnlineLink(CreateMixin, UpdateMixin, SoftDeleteMixin):
    class_room = models.ForeignKey(LessonCourse, on_delete=models.CASCADE, related_name="online_link")
    link = models.URLField()
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = "online_link"


class Question(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(max_length=255)
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = "poll_question"


class SectionQuestion(CreateMixin, UpdateMixin, SoftDeleteMixin):
    question_title = models.CharField(max_length=255, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="section_question",
                                limit_choices_to={"is_publish": True})
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = "section_question"


class AnswerQuestion(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_poll_answer")
    section_question = models.ForeignKey(SectionQuestion, on_delete=models.CASCADE, related_name="section_question")
    rate = models.CharField(choices=RateChoices.choices)

    class Meta:
        db_table = "poll_answer"


class CallLessonCourse(CreateMixin, UpdateMixin, SoftDeleteMixin):
    lesson_course = models.ForeignKey(LessonCourse, on_delete=models.CASCADE, related_name="call")
    call = models.CharField(max_length=50, help_text=_("تماس"))
    status = models.CharField(max_length=13, help_text=_("وضعیت تماس"), choices=CallStatusChoices.choices)
    call_answering = models.CharField(max_length=20, help_text=_("پاسخگوی تماس"))
    project = models.CharField(max_length=30, help_text=_("بابت پروژه"))
    call_date = models.DateField(help_text=_("تاریخ مکالمه"))
    result_call = models.TextField(help_text=_("نتیجه مکالمه"))
    cancellation_alert = models.BooleanField(default=False, help_text=_("هشدار انصراف"))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_call", null=True)

    class Meta:
        db_table = "call_lesson_course"


class SignupCourse(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_signup")
    student_name = models.CharField(max_length=120, help_text="نام و نام خوادگی داشن اموز")
    phone_number = models.CharField(max_length=15, help_text="شماره تلفن ")
    referral_code = models.CharField(max_length=30, blank=True)

    class Meta:
        db_table = "course_signup"
