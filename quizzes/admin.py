from django.contrib import admin

from .models import Category, Choice, Question, Quiz


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'emoji', 'quiz_count')
    prepopulated_fields = {'slug': ('name',)}

    def quiz_count(self, obj):
        return obj.quizzes.count()

    quiz_count.short_description = 'Quizzes'


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'duration_minutes', 'is_published', 'questions_count')
    list_filter = ('category', 'difficulty', 'is_published')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [QuestionInline]
    list_editable = ('is_published',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz',)
    search_fields = ('text',)
    inlines = [ChoiceInline]
