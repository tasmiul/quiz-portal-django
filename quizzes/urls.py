from django.urls import path

from . import views

urlpatterns = [
    path('categories/', views.categories, name='api-categories'),
    path('home/', views.home, name='api-home'),
    path('quizzes/', views.quizzes, name='api-quizzes'),
    path('quizzes/<int:quiz_id>/', views.quiz_detail, name='api-quiz-detail'),
    path('quizzes/<int:quiz_id>/submit/', views.submit_quiz, name='api-quiz-submit'),
]