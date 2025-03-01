from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from accounts.models import Student
from exam_app.models import Exam, Question, Answer, Score


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ["id", "get_course_name", "name", "created_at", "description", "exam_end_date"]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', "exam", "name"]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', "answer", "created_at"]

    def create(self, validated_data):
        student = validated_data.pop("get_student")
        return Answer.objects.create(question_id=self.context['question_pk'], student=student, **validated_data)

    def validate(self, attrs):
        try:
            get_student = Student.objects.get(user=self.context['request'].user)
        except Student.DoesNotExist:
            raise serializers.ValidationError({"user": "student can send answer"})
        attrs['get_student'] = get_student
        return attrs


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['id', "exam", "score", "created_at"]
