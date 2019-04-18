from django.shortcuts import render

# Create your views here.

def course_index(request):
    """
    课堂app页
    :param request:
    :return:
    """
    return render(request, 'course/course.html')