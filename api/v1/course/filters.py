import django_filters

from apps.course_app.enums import ProgresChoices
from apps.course_app.models import LessonCourse


class LessonCourseFilter(django_filters.FilterSet):
    class_name = django_filters.CharFilter(field_name='class_name', lookup_expr='icontains')
    progress = django_filters.MultipleChoiceFilter(choices=ProgresChoices.choices)

    class Meta:
        model = LessonCourse
        fields = (
            'class_name',
            'progress'
        )
