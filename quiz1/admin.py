from django.contrib import admin
from .models import Category1,Quiz1,Question,Choice,QuizSubmission,UserRank
# Register your models here.
admin.site.register(Category1)
admin.site.register(Quiz1)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(QuizSubmission)
admin.site.register(UserRank)