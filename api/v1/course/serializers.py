from rest_framework.serializers import ModelSerializer, SerializerMethodField, PrimaryKeyRelatedField, IntegerField
from rest_framework.generics import get_object_or_404

from course.models import Course, Term, UnitSelection
from departments.models import Department


class TermSerializer(ModelSerializer):
    department_name = SerializerMethodField()
    department = PrimaryKeyRelatedField(queryset=Department.objects.select_related('user'))

    class Meta:
        model = Term
        fields = '__all__'

    def get_department_name(self, obj):
        return obj.department.department_name


class CourseSerializer(ModelSerializer):
    department = PrimaryKeyRelatedField(queryset=Department.objects.select_related('user'))
    department_name = SerializerMethodField()
    term_name = SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_department_name(self, obj):
        return obj.department.department_name

    def get_term_name(self, obj):
        term = obj.term
        return f'{term.start_date} || {term.end_date} || {term.term_number}'


class UnitSelectionSerializer(ModelSerializer):
    student_name = SerializerMethodField()
    term_name = SerializerMethodField()
    professor_name = SerializerMethodField()
    course_name = SerializerMethodField()

    class Meta:
        model = UnitSelection
        fields = '__all__'

    def get_student_name(self, obj):
        return obj.student.get_full_name

    def get_term_name(self, obj):
        term = obj.term
        return f'{term.start_date} || {term.end_date} || {term.term_number}'

    def get_professor_name(self, obj):
        return obj.professor.get_full_name

    def get_course_name(self, obj):
        return obj.course.course_name
