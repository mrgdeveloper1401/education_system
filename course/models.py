from django.db import models
from django.utils.translation import gettext_lazy as _
from treebeard.mp_tree import MP_Node

from core.models import UpdateMixin, CreateMixin, SoftDeleteMixin


class Term(CreateMixin, UpdateMixin, SoftDeleteMixin):
    department = models.ForeignKey('departments.Department', on_delete=models.PROTECT, related_name='department_term',
                                   limit_choices_to={"user__is_staff": True, "user__is_active": True},
                                   verbose_name=_("دپارتمان"))
    start_date = models.DateField(_("تاریخ شروع"))
    end_date = models.DateField(_("تاریخ پایان"))
    term_number = models.CharField(_("شماره ترم"), max_length=10)

    def __str__(self):
        return f"{self.start_date} || {self.end_date} || {self.term_number}"

    class Meta:
        db_table = 'term'
        verbose_name = _("ترم")
        verbose_name_plural = _("ترم ها")
        ordering = ('-created_at',)


class Course(CreateMixin, UpdateMixin, SoftDeleteMixin):
    department = models.ForeignKey("departments.Department", on_delete=models.PROTECT,
                                   related_name='course_department', verbose_name=_("دپارتمان"))
    term = models.ForeignKey(Term, on_delete=models.PROTECT, related_name='course_term')
    course_name = models.CharField(_("نام درس"), max_length=30)
    is_publish = models.BooleanField(_('حالت انتشار'), default=True)
    image = models.ImageField(_("عکس دوره"), upload_to='course/course_image/%Y/%m/%d')

    def __str__(self):
        return self.course_name

    class Meta:
        db_table = 'course'
        verbose_name = _("درس")
        verbose_name_plural = _("درس ها")
        ordering = ('-created_at',)


class UnitSelection(CreateMixin, UpdateMixin, SoftDeleteMixin):
    term = models.ForeignKey("course.Term", on_delete=models.PROTECT, related_name='unit_selection_term',
                             verbose_name=_("ترم"))
    professor = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='unit_selection_professor',
                                  verbose_name=_("استاد"), limit_choices_to={"is_active": True, "is_coach": True})
    course = models.ForeignKey(Course, models.PROTECT, related_name='unit_selection_courses', verbose_name=_("درس"),
                               limit_choices_to={"is_publish": True})
    student = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='student',
                                limit_choices_to={"is_student": True})

    class Meta:
        db_table = 'unit_selection'
        verbose_name = _("انتخاب درس")
        verbose_name_plural = _("انتخاب درس ها")
        ordering = ('-created_at',)
        unique_together = (("term", "student",),)