from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin


class Exam(CreateMixin, UpdateMixin, SoftDeleteMixin):
    name = models.CharField(max_length=255, help_text=_("نام ازمون"))
    description = models.TextField(help_text=_("توضیح در مورد ازمون"), null=True)
    course = models.ForeignKey("course.Course", on_delete=models.DO_NOTHING, related_name="exams")
    is_active = models.BooleanField(default=True)
    start_datetime = models.DateTimeField(help_text=_("تاریخ شروع ازمون"))
    number_of_time = models.PositiveSmallIntegerField(help_text=_("مدت زمان ازمون بر اساس دقیقه"))

    def __str__(self):
        return self.name

    @property
    def is_done_exam(self):
        return self.start_datetime < timezone.now()

    @property
    def exam_end_date(self):
        return self.start_datetime + timezone.timedelta(minutes=self.number_of_time)

    @property
    def get_course_name(self):
        return self.course.course_name

    class Meta:
        db_table = 'exam'


class Question(CreateMixin, UpdateMixin, SoftDeleteMixin):
    name = models.TextField(help_text=_("سوال"))
    exam = models.ForeignKey(Exam, on_delete=models.DO_NOTHING, related_name="questions")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'question'


class Participation(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey('accounts.Student', on_delete=models.DO_NOTHING, related_name="participation_student")
    exam = models.ForeignKey(Exam, on_delete=models.DO_NOTHING, related_name="participation_exam")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'participation'
        unique_together = (('student', 'exam'),)


class Answer(CreateMixin, UpdateMixin, SoftDeleteMixin):
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, related_name="answers")
    student = models.ForeignKey('accounts.Student', on_delete=models.DO_NOTHING, related_name="student_answers")
    answer = models.TextField(help_text=_("جواب ازمون"))
    is_active = models.BooleanField(default=True)
    student_ip_address = models.GenericIPAddressField(null=True, blank=True, help_text=_("ادرس ای پی کاربر"))

    class Meta:
        unique_together = (('question', 'student'),)
        db_table = 'answer'


class Score(CreateMixin, UpdateMixin, SoftDeleteMixin):
    exam = models.ForeignKey(Exam, on_delete=models.DO_NOTHING, related_name="scores")
    student = models.ForeignKey('accounts.Student', on_delete=models.DO_NOTHING, related_name="student_scores")
    score = models.FloatField(validators=[MinValueValidator(0)], help_text=_("نمره کاربر"), null=True,
                              blank=True)

    class Meta:
        db_table = 'score'
