from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Course, Enrollment, Question, Choice, Submission
import logging

logger = logging.getLogger(__name__)


def submit(request, course_id):

    course = get_object_or_404(Course, pk=course_id)

    user = request.user

    enrollment = get_object_or_404(
        Enrollment,
        user=user,
        course=course
    )

    submission = Submission.objects.create(
        enrollment=enrollment
    )

    selected_ids = extract_answers(request)

    selected_choices = Choice.objects.filter(
        id__in=selected_ids
    )

    submission.choices.set(selected_choices)

    return HttpResponseRedirect(
        reverse(
            'onlinecourse:exam_result',
            args=(course_id, submission.id)
        )
    )


def extract_answers(request):

    selected_ids = []

    for key in request.POST:

        if key.startswith('choice_'):

            selected_ids.append(
                int(request.POST[key])
            )

    return selected_ids


def show_exam_result(request, course_id, submission_id):

    course = get_object_or_404(
        Course,
        pk=course_id
    )

    submission = get_object_or_404(
        Submission,
        id=submission_id
    )

    selected_ids = list(
        submission.choices.values_list(
            'id',
            flat=True
        )
    )

    total_score = 0
    possible_score = 0

    for question in course.question_set.all():

        possible_score += question.grade

        if question.is_get_score(selected_ids):

            total_score += question.grade

    grade = 0

    if possible_score > 0:

        grade = int(
            total_score * 100 / possible_score
        )

    context = {
        'course': course,
        'submission': submission,
        'selected_ids': selected_ids,
        'grade': grade,
        'possible': possible_score,
        'total_score': total_score
    }

    return render(
        request,
        'onlinecourse/exam_result_bootstrap.html',
        context
    )


def registration_request(request):

    context = {}

    if request.method == 'GET':

        return render(
            request,
            'onlinecourse/user_registration_bootstrap.html',
            context
        )

    elif request.method == 'POST':

        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        user_exist = False

        try:
            User.objects.get(username=username)
            user_exist = True

        except:
            logger.error("New user")

        if not user_exist:

            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

            login(request, user)

            return redirect("onlinecourse:index")

        else:

            context['message'] = "User already exists."

            return render(
                request,
                'onlinecourse/user_registration_bootstrap.html',
                context
            )


def login_request(request):

    context = {}

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['psw']

        user = authenticate(
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('onlinecourse:index')

        else:

            context['message'] = "Invalid username or password."

            return render(
                request,
                'onlinecourse/user_login_bootstrap.html',
                context
            )

    return render(
        request,
        'onlinecourse/user_login_bootstrap.html',
        context
    )


def logout_request(request):

    logout(request)

    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):

    if not user.is_authenticated:

        return False

    return Enrollment.objects.filter(
        user=user,
        course=course
    ).exists()


class CourseListView(generic.ListView):

    template_name = 'onlinecourse/course_list_bootstrap.html'

    context_object_name = 'course_list'

    def get_queryset(self):

        user = self.request.user

        courses = Course.objects.order_by(
            '-total_enrollment'
        )[:10]

        for course in courses:

            course.is_enrolled = check_if_enrolled(
                user,
                course
            )

        return courses


class CourseDetailView(generic.DetailView):

    model = Course

    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):

    course = get_object_or_404(
        Course,
        pk=course_id
    )

    user = request.user

    if user.is_authenticated:

        if not check_if_enrolled(user, course):

            Enrollment.objects.create(
                user=user,
                course=course,
                mode='honor'
            )

            course.total_enrollment += 1
            course.save()

    return HttpResponseRedirect(
        reverse(
            'onlinecourse:course_details',
            args=(course.id,)
        )
    )
