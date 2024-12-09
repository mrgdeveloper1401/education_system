from rest_framework.serializers import ModelSerializer, SerializerMethodField

from course.models import Course, Term, UnitSelection


class TermSerializer(ModelSerializer):

    class Meta:
        model = Term
        exclude = ['is_deleted', "deleted_at"]


class CourseSerializer(ModelSerializer):
    term_name = SerializerMethodField()

    class Meta:
        model = Course
        exclude = ['deleted_at', "is_deleted"]
        extra_kwargs = {"term": {'read_only': True}}

    def get_term_name(self, obj):
        term = obj.term
        return f'{term.start_date} || {term.end_date} || {term.term_number}'

    def create(self, validated_data):
        term_id = self.context['term_pk']
        return Course.objects.create(term_id=term_id, **validated_data)


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
