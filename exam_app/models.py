from datetime import timedelta
import pytz
from django.conf import settings
from rest_framework import exceptions as rest_framework_exceptions
from django.core import exceptions
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from accounts.models import User
from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from exam_app.enums import QuestionType


class Exam(CreateMixin, UpdateMixin, SoftDeleteMixin):
    name = models.CharField(max_length=255, help_text=_("نام ازمون"))
    description = models.TextField(help_text=_("توضیح در مورد ازمون"))
    course = models.ForeignKey("course.Course", on_delete=models.DO_NOTHING, related_name="exam",
                               blank=True, null=True,
                               help_text=_("میتوان دوه ای را انتخاب کرد یا ازمون به دوره خاصی مربوط نباشد"))
    is_active = models.BooleanField(default=True)
    start_datetime = models.DateTimeField( blank=True, null=True,
        help_text=_("تاریخ شروع ازمون میتوانید از یک زمان خاصی بگید ازمون شروع شود یا میتوان ان را خالی گذاشت"))
    number_of_time = models.PositiveSmallIntegerField(help_text=_("مدت زمان ازمون بر اساس دقیقه"))
    user_access = models.ManyToManyField(User, related_name="user_access", blank=True)
    coach_access = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="user_coach_exam_access",
        blank=True,
        null=True,
        limit_choices_to={
            "is_coach": True
        }
    )

    def __str__(self):
        return self.name

    def get_exam_question_count(self):
        return self.questions.count()

    @property
    def is_exam_start(self):
        return self.start_datetime < timezone.now() if self.start_datetime else None

    @property
    def is_done_exam(self):
        if self.exam_end_date is None:
            return None
        else:
            if self.exam_end_date > timezone.now():
                return False
            return True

    @property
    def exam_end_date(self):
        if self.start_datetime:
            d = (self.start_datetime + timedelta(minutes=self.number_of_time))
            d = d.astimezone(tz=pytz.timezone(settings.TIME_ZONE))
            return d
        return None

    def clean(self):
        if self.course and not self.start_datetime:
            raise exceptions.ValidationError(
                {"course": _("اگه دوره ای رو انتخاب میکنید باید تایم شروع ان را هم ست کنید")}
            )

    class Meta:
        db_table = 'exam'
        ordering = ("-id",)


class Question(CreateMixin, UpdateMixin, SoftDeleteMixin):
    name = models.TextField(help_text=_("سوال"))
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name="questions")
    is_active = models.BooleanField(default=True)
    question_file = models.FileField(
        upload_to="question_exam/file/%Y/%m/%d",
        blank=True,
        null=True,
        help_text=_("پیوست یک فایل برای سوال"
                    "فورمت های مجاز"
                    "zip - pdf - png - jpeg"),
        validators=(FileExtensionValidator(allowed_extensions=("zip","pdf", "png", "jpeg")),)
    )
    question_type = models.CharField(
        max_length=2,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
        help_text=_("نوع سوال")
    )
    max_score = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text=_("حداکثر نمره قابل کسب برای این سوال")
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'question'


class Participation(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey('accounts.Student', on_delete=models.DO_NOTHING, related_name="participation_student")
    exam = models.ForeignKey(Exam, on_delete=models.DO_NOTHING, related_name="participation_exam")
    is_access = models.BooleanField(default=True)
    score = models.FloatField(_("نمره"), blank=True, null=True)

    class Meta:
        db_table = 'participation'

    @property
    def expired_exam(self):
        return self.created_at + timedelta(minutes=self.exam.number_of_time)


class Choice(CreateMixin, UpdateMixin, SoftDeleteMixin):
    question = models.ForeignKey(
        Question,
        on_delete=models.DO_NOTHING,
        related_name='choices',
        limit_choices_to={'question_type': QuestionType.MULTIPLE_CHOICE}
    )
    text = models.CharField(max_length=255, help_text=_("متن گزینه"))
    is_correct = models.BooleanField(default=False, help_text=_("آیا این گزینه صحیح است؟"))

    class Meta:
        db_table = 'choice'
        ordering = ('id',)


class Answer(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="user_answer"
    )
    participation = models.ForeignKey(
        'Participation',
        on_delete=models.DO_NOTHING,
        related_name='participation_answer'
    )
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, related_name="question_answer")

    # برای سوالات چندگزینه‌ای
    selected_choices = models.ManyToManyField(Choice, blank=True)

    # برای سوالات تشریحی
    text_answer = models.TextField(blank=True, null=True)

    # نمره اختصاص داده شده
    given_score = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=_("نمره اختصاص داده شده توسط تصحیح کننده")
    )

    # is_corrected = models.BooleanField(default=False, help_text=_("آیا تصحیح شده است؟"))
    choice_file = models.FileField(upload_to="choice_exam/file/%Y/%m/%d", blank=True, null=True,
                                   help_text=_("در صورتی که نیاز به ارسال فایل هست میتوانید فایل رو ارسال کیند"))

    class Meta:
        db_table = 'answer'

    def save(self, *args, **kwargs):
        if self.given_score:
            if self.given_score > self.question.max_score:
                raise rest_framework_exceptions.ValidationError(
                    {
                        "message": _("given score can not biggest question_max_score")
                    }
                )
        super().save(*args, **kwargs)
