from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers, exceptions
from django.utils.translation import gettext_lazy as _

from accounts.models import Student, User
from course.models import Course
from exam_app.models import Exam, Question, Participation, Choice, Answer


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
            "is_exam_start",
            "start_datetime",
            "get_exam_question_count",
            "is_active"
        )

    def to_representation(self, instance):
        request = self.context.get("request")

        data = super().to_representation(instance)

        if request.user.is_coach is False and request.user.is_staff is False:
            data.pop("is_active", None)

        return data


class UserAccessAdminCoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "mobile_phone",
            "get_full_name"
        )


class CoachAdminExamSerializer(serializers.ModelSerializer):
    user_access = UserAccessAdminCoachSerializer(many=True)
    coach_access = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            is_coach=True,
            is_active=True
        ).only(
            "mobile_phone",
            "first_name",
            "last_name"
        )
    )

    class Meta:
        model = Exam
        fields = (
            "id",
            "name",
            "description",
            "exam_end_date",
            "number_of_time",
            "is_done_exam",
            "start_datetime",
            "get_exam_question_count",
            "user_access",
            "is_active",
            "coach_access"
        )


class CreateExamSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_publish=True).only(
            "course_name"
        ),
        required=False
    )
    user_access = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True).only(
                "mobile_phone",
                "first_name",
                "last_name"
        ),
        many=True,
        required=False
    )
    coach_access = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_coach=True).only("mobile_phone")
    )

    class Meta:
        model = Exam
        exclude = ("is_deleted", "deleted_at", "updated_at")


class QuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = (
            "id",
            "text"
        )


class CreateChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = (
            "id",
            "text",
            "is_correct"
        )

    def create(self, validated_data):
        question_pk = self.context.get("question_pk")
        return Choice.objects.create(question_id=question_pk, **validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    choices = QuestionChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', "name", "question_file", "max_score", "question_type", "choices")

    def create(self, validated_data):
        exam_id = self.context['exam_pk']
        return Question.objects.create(exam_id=exam_id, **validated_data)


class ExamNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ("name",)


class ParticipationSerializer(serializers.ModelSerializer):
    exam = serializers.StringRelatedField(read_only=True)
    exam_time = serializers.SerializerMethodField()
    is_done = serializers.SerializerMethodField()
    exam_questions_count = serializers.SerializerMethodField()
    user_answer_count = serializers.SerializerMethodField()

    def get_exam_time(self, obj):
        return obj.exam.number_of_time

    @extend_schema_field(serializers.IntegerField())
    def get_exam_questions_count(self, obj):
        return obj.exam_questions_count

    @extend_schema_field(serializers.IntegerField())
    def get_user_answer_count(self, obj):
        return obj.user_answer_count

    @extend_schema_field(serializers.BooleanField())
    def get_is_done(self, obj):
        return obj.exam.is_done_exam

    class Meta:
        model = Participation
        fields = (
            "id",
            "student",
            "exam",
            "created_at",
            "is_access",
            "score",
            "created_at",
            "expired_exam",
            "exam_time",
            "is_done",
            "exam_questions_count",
            "user_answer_count"
        )
        read_only_fields = ("student", 'is_access', "score")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        coach_user = self.context['request'].user.is_coach
        admin_user = self.context['request'].user.is_staff

        if coach_user or admin_user:
            data.pop("user_answer_count", None)
            data.pop("exam_questions_count", None)
        return data

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


class ParticipationCoachSerializer(serializers.ModelSerializer):
    exam = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Participation
        fields = (
            "id",
            "student",
            "exam",
            "created_at",
            "is_access",
            "score"
        )
        read_only_fields = ("student", 'is_access')


class AnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.only(
            "name"
        ).filter(
            is_active=True
        ),
    )
    selected_choices = serializers.PrimaryKeyRelatedField(
        queryset=Choice.objects.only(
            "is_correct"
        ),
        many=True,
        required=False
    )
    class Meta:
        model = Answer
        fields = (
            "id",
            "question",
            "selected_choices",
            "text_answer",
            "given_score",
            "choice_file",
            "created_at"
        )
        read_only_fields = ("given_score", "participation")

    def validate(self, attrs):
        participation_pk = int(self.context['participation_pk'])
        user_id = int(self.context['request'].user.id)
        exam_pk = int(self.context['exam_pk'])

        # get participation
        participation = Participation.objects.filter(
            id=participation_pk,
            student__user_id=user_id,
            exam_id=exam_pk,
        ).select_related(
            "exam"
        ).only(
            "id",
            "exam__start_datetime",
            "exam__number_of_time"
        )
        p_first = participation.first()  # get object

        # check send duplicat question
        if self.instance is None:
            if Answer.objects.filter(
                user_id=user_id,
                participation_id=participation_pk,
                question=attrs.get("question"),
            ).exists():
                raise serializers.ValidationError(
                    {
                        "message": _("you already have question please edit")
                    }
                )

        # check user exists in exam
        if not p_first.exam.user_access.filter(id=user_id).exists():
            raise exceptions.PermissionDenied()

        # check participation dose exiting
        if not participation.exists():
            raise exceptions.ValidationError(
                {
                    "message": _("participation is not exits")
                }
            )
        else:
            # check dose exam is done or not
            if p_first.exam.is_done_exam: # exam is done
                raise exceptions.ValidationError(
                    {
                        "message": _("exam is done!")
                    }
                )
            if p_first.exam.is_exam_start is False: # exam not start
                raise exceptions.ValidationError(
                    {
                        "message": _("exam not started!")
                    }
                )

        return attrs

    def create(self, validated_data):
        participation_pk = int(self.context['participation_pk'])
        selected_choices = validated_data.pop("selected_choices", [])
        user_id = int(self.context['request'].user.id)
        answer = Answer.objects.create(
            participation_id=participation_pk,
            user_id=user_id,
            **validated_data
        )

        if selected_choices:
            answer.selected_choices.set(selected_choices)

        return answer


class AnswerScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'given_score', 'question', 'participation')
        read_only_fields = ('question', 'participation')

    def validate_given_score(self, value):
        question = self.instance.question
        if value > question.max_score:
            raise serializers.ValidationError(
                {
                    "message": _("نمره وارد شده بیشتر از نمره مجاز برای این سوال است.")
                }
            )
        return value


class ParticipationListRetrieveSerializer(serializers.ModelSerializer):
    student_get_full_name = serializers.SerializerMethodField()
    exam_questions_count = serializers.SerializerMethodField()
    user_answer_count = serializers.SerializerMethodField()
    percentage_answered = serializers.SerializerMethodField()

    def get_student_get_full_name(self, obj):
        return obj.student.user.get_full_name

    def get_exam_questions_count(self, obj):
        return obj.exam_questions_count

    def get_user_answer_count(self, obj):
        return obj.user_answer_count

    def get_percentage_answered(self, obj):
        if obj.exam_questions_count == 0:
            return 0
        return round(
            (obj.user_answer_count / obj.exam_questions_count) * 100, 2
        )

    class Meta:
        model = Participation
        fields = (
            "id",
            "score",
            "student_get_full_name",
            "exam_questions_count",
            "user_answer_count",
            "percentage_answered"
        )


class CoachUserAnswerSelectedChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = (
            "id",
            "text",
            "is_correct"
        )


class CoachUserAnswerSerializer(serializers.ModelSerializer):
    question_name = serializers.SerializerMethodField()
    question_max_score = serializers.SerializerMethodField()
    selected_choices = CoachUserAnswerSelectedChoiceSerializer(many=True, read_only=True)

    def get_question_name(self, obj):
        return obj.question.name

    def get_question_max_score(self, obj):
        return obj.question.max_score

    class Meta:
        model = Answer
        fields = (
            "id",
            "text_answer",
            "given_score",
            "choice_file",
            "question_name",
            "question_id",
            "question_max_score",
            "selected_choices"
        )
        read_only_fields = (
            "text_answer",
            "choice_file",
            "question_name",
            "question_max_score",
        )
