from rest_framework.serializers import ModelSerializer, SerializerMethodField

from course.models import Course, Term, UnitSelection


class TermSerializer(ModelSerializer):

    class Meta:
        model = Term
        fields = '__all__'


class CourseSerializer(ModelSerializer):
    term_name = SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

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
