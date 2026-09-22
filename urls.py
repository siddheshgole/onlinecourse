from django.urls import path
from . import views

urlpatterns = [
    path('submit/<int:lesson_id>/', views.submit, name='submit'),
    path('exam_result/<int:lesson_id>/', views.show_exam_result, name='show_exam_result'),
]
