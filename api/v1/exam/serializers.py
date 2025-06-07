from django.utils import timezone
from rest_framework import serializers, exceptions
from django.utils.translation import gettext_lazy as _

from accounts.models import Student
from exam_app.models import Exam, Question, Answer, Score, Participation


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = (
            "id",
            "name",
            "description",
            "exam_end_date",
            "number_of_time",
            "is_done_exam",
            "start_datetime"
        )


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', "name")


class ExamNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ("name",)


class ParticipationSerializer(serializers.ModelSerializer):
    exam = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Participation
        fields = (
            "student",
            "exam",
            "created_at",
            "is_access"
        )
        read_only_fields = ("student", 'is_access')

    def create(self, validated_data):
        return Participation.objects.create(
            student_id=self.context["request"].user.student.id,
            exam_id=self.context["exam_pk"],
            **validated_data
        )

    def validate(self, attrs):
        user_id = self.context["request"].user.id
        exam_id = self.context["exam_pk"]

        exam = Exam.objects.filter(
            id=exam_id,
            user_access__id=user_id
        ).only("name", "start_datetime", "number_of_time")

        # get object exam
        get_exam = exam.first()

        # check user already taken this exam
        if Participation.objects.filter(exam_id=exam_id, student__user_id=user_id).exists():
            raise exceptions.ValidationError({"message": _("You have already taken the test.")})

        # exam not exists
        if not exam.exists():
            raise exceptions.ValidationError({"message": _("you not access this exam")})

        # exam not start
        if (get_exam and get_exam.start_datetime) and (get_exam.start_datetime > timezone.now()):
            raise exceptions.ValidationError({"message": _("exam not started")})

        # exam is done
        if get_exam.is_done_exam:
            raise exceptions.ValidationError({"message": _("exam is already done")})

        # check user is student yes or no
        if not Student.objects.filter(user_id=user_id).only("student_number").exists():
            raise exceptions.ValidationError({"message": _("your account not student")})

        return attrs


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', "answer", "created_at")

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
        fields = ('id', "exam", "score", "created_at")
