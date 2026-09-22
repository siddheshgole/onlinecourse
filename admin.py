from django.contrib import admin
from .models import Course, Lesson, Question, Choice, Submission, Instructor, Learner


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text']
    inlines = [ChoiceInline]


class LessonAdmin(admin.ModelAdmin):
    list_display = ['name', 'course']
    inlines = [QuestionInline]


admin.site.register(Course)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
admin.site.register(Instructor)
admin.site.register(Learner)
