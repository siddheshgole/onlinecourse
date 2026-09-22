from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lesson, Question, Choice, Submission


def submit(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = Question.objects.filter(lesson=lesson)
    score = 0

    if request.method == 'POST':
        for question in questions:
            selected_choice = request.POST.get(str(question.id))
            if selected_choice:
                choice = Choice.objects.get(id=selected_choice)
                if choice.is_correct:
                    score += 1

        Submission.objects.create(
            user=request.user,
            lesson=lesson,
            score=score
        )

        return redirect('show_exam_result', lesson_id=lesson.id)

    return render(request, 'onlinecourse/exam.html', {
        'lesson': lesson,
        'questions': questions
    })


def show_exam_result(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    submission = Submission.objects.filter(
        user=request.user,
        lesson=lesson
    ).order_by('-submitted_at').first()

    return render(request, 'onlinecourse/exam_result.html', {
        'lesson': lesson,
        'submission': submission
    })
