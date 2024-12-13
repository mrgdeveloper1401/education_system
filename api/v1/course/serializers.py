from rest_framework import serializers
from course.models import Course, Term


class TermSerializer(serializers.ModelSerializer):

    class Meta:
        model = Term
        fields = ['id', "term_name"]


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ['deleted_at', "is_deleted"]
