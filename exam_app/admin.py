from django.contrib import admin

from . import models
# Register your models here.


admin.site.register(models.Exam)
admin.site.register(models.Question)
admin.site.register(models.Answer)
admin.site.register(models.Score)
