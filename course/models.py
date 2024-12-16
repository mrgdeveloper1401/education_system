from django.db import models
from core.models import UpdateMixin, CreateMixin, SoftDeleteMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator

from utils.file_name import course_name, practice_name, section_name
from utils.validators import file_upload_validator


class Term(CreateMixin, UpdateMixin, SoftDeleteMixin):
    term_name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.term_name

    class Meta:
        db_table = 'term'
        verbose_name = _("ترم")
        verbose_name_plural = _("ترم ها")


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
        verbose_name = _("درس")
        verbose_name_plural = _("درس ها")


class Section(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='sections')
    video = models.FileField(upload_to=section_name,
                             validators=[FileExtensionValidator(["mp4"]), file_upload_validator])
    video_title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(db_default=True)

    class Meta:
        ordering = ('created_at',)
        db_table = 'course_section'
        verbose_name = _("قسمت")
        verbose_name_plural = _("قسمت های دوره")


class LessonTakenByStudent(CreateMixin, SoftDeleteMixin):
    student = models.ForeignKey("accounts.Student", related_name='lesson_student', on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='course_product')

    def __str__(self):
        return f'course is: {self.course.course_name} student is: {self.student.user.get_full_name}'

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
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name="course_score")
    coach = models.ForeignKey('accounts.Coach', related_name='coach_score', on_delete=models.DO_NOTHING)
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(20)],
                                             help_text=_("حداکثر نمره برابر با 20"
                                                         "حداقل نمره برابر با 0 است"))

    class Meta:
        db_table = 'score'
        verbose_name = _("نمره")
        verbose_name_plural = _("نمره ها")


class Comment(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.ForeignKey('accounts.Student', on_delete=models.DO_NOTHING, related_name='student_comments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    comment_body = models.TextField(_("متن کامنت"))
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = 'comment'
        verbose_name = _("نظر")
        verbose_name_plural = _("نظرات")


class Practice(CreateMixin, UpdateMixin, SoftDeleteMixin):
    coach = models.ForeignKey('accounts.Coach', on_delete=models.DO_NOTHING, related_name='practice')
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name="course_practice")
    practice_file = models.FileField(upload_to=practice_name)
    practice_title = models.CharField(_("عنوان تمرین"), max_length=255)
    is_available = models.BooleanField(default=False)
    expired_practice = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.practice_title

    class Meta:
        db_table = 'practice'
        verbose_name = _("تمرین")
        verbose_name_plural = _("تمرین ها")


class PracticeSubmission(CreateMixin, UpdateMixin, SoftDeleteMixin):
    practice = models.ForeignKey(Practice, on_delete=models.DO_NOTHING, related_name='submissions')
    student = models.ForeignKey("accounts.Student", on_delete=models.DO_NOTHING, related_name='submission_student')
    upload_file = models.FileField(upload_to="submit_practice/%Y/%m/%d/%H:%M:%S")
    grade = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)

    def __str__(self):
        return f'{self.grade} {self.student.user.get_full_name}'

    class Meta:
        db_table = 'submission'
        verbose_name = _("ارسال تکلیف")
        verbose_name_plural = _("تکالیف ارسال شده")


class Quiz(CreateMixin, UpdateMixin, SoftDeleteMixin):
    coach = models.ForeignKey('accounts.Coach', on_delete=models.DO_NOTHING, related_name='coach_quiz')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='quizzes')
    quiz_time = models.DateTimeField(help_text=_("تاریخ ازمون"))
    duration = models.DurationField(help_text=_("زمان ازمون"))

    def __str__(self):
        return f'{self.title}'

    class Meta:
        db_table = 'quiz'
        verbose_name = _("ازمون")
        verbose_name_plural = _("ازمون ها")


class Question(CreateMixin, UpdateMixin, SoftDeleteMixin):
    quiz = models.ForeignKey(Quiz, on_delete=models.DO_NOTHING, related_name="quiz_questions")
    question = models.TextField(help_text=_("عنوان سوال"))

    def __str__(self):
        return self.quiz.title

    class Meta:
        db_table = 'question'
        verbose_name = _("سوال")
        verbose_name_plural = _("سوال ها")


class ClassRoom(CreateMixin, UpdateMixin, SoftDeleteMixin):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name="course_classroom")
    student = models.ManyToManyField('accounts.Student', related_name="class_room_user")
    coach = models.ManyToManyField('accounts.Coach', related_name='class_room_coach')
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'class_room'
        verbose_name = _("کلاس درسی")
        verbose_name_plural = _("کلاس های درسی")
