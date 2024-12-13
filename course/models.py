from django.db import models
from core.models import UpdateMixin, CreateMixin, SoftDeleteMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class Term(CreateMixin, UpdateMixin, SoftDeleteMixin):
    term_name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.term_name

    class Meta:
        db_table = 'term'
        verbose_name = _("ترم")


class Course(CreateMixin, UpdateMixin, SoftDeleteMixin):
    term = models.ForeignKey(Term, on_delete=models.DO_NOTHING, related_name='courses')
    course_name = models.CharField(max_length=100)
    course_description = models.TextField()
    course_price = models.FloatField()
    course_duration = models.PositiveSmallIntegerField()
    course_image = models.ImageField(upload_to="course_image/%Y/%m/%d")

    def __str__(self):
        return self.course_name

    class Meta:
        db_table = 'course'


class LessonTakenByStudent(CreateMixin, SoftDeleteMixin):
    student = models.ForeignKey("accounts.Student", related_name='lesson_student', on_delete=models.DO_NOTHING)
    coach = models.ManyToManyField('accounts.Coach', related_name='lesson_user_coach')
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='course_product')

    class Meta:
        db_table = 'lesson_student'
        verbose_name = _("اخذ")
        verbose_name_plural = _("درس های اخذ شده دانشجو")


class LessonTakenByCoach(CreateMixin, SoftDeleteMixin):
    coach = models.ForeignKey("accounts.Coach", related_name='lesson_provide_coach', on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lesson_coach_course')

    class Meta:
        db_table = 'lesson_coach'
        verbose_name = _("اخذ")
        verbose_name_plural = _("درس های اخذ شده مربی")


class Score(models.Model):
    student = models.ForeignKey("accounts.Student", related_name='student_score', on_delete=models.DO_NOTHING)
    coach = models.ForeignKey('accounts.Coach', related_name='coach_score', on_delete=models.DO_NOTHING)
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(20)],
                                             help_text=_("حداکثر نمره برابر با 20"
                                                         "حداقل نمره برابر با 0 است"))

    class Meta:
        db_table = 'score'
        verbose_name = _("نمره")
        verbose_name_plural = _("نمره ها")


class Comment(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.DO_NOTHING, related_name='student_comments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    comment_body = models.TextField(_("متن کامنت"))
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = 'comment'
        verbose_name = _("نظر")
        verbose_name_plural = _("نظرات")


class Practice(models.Model):
    # coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='practice')
    practice_file = models.FileField(upload_to='practice/%Y/%m/%d')

    class Meta:
        db_table = 'practice'
