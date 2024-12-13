from django.contrib import admin
from . import models


admin.site.register(models.Course)
admin.site.register(models.Term)
admin.site.register(models.LessonTakenByCoach)
admin.site.register(models.LessonTakenByStudent)
admin.site.register(models.Comment)
admin.site.register(models.Practice)
