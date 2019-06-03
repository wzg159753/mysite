import logging

from django.http import Http404
from django.views import View
from django.shortcuts import render

from . import models
# Create your views here.

logger = logging.getLogger('django')

def course_index(request):
    """
    课堂app页
    /course/
    :param request:
    :return:
    """
    courses = models.Course.objects.select_related('teacher').only('title', 'cover_url', 'teacher__name', 'teacher__positional_title').filter(is_delete=False)
    return render(request, 'course/course.html', locals())


class CourseDetailView(View):
    """
    /course/<int:course_id>/
    """
    def get(self, request, course_id):
        try:
            course = models.Course.objects.select_related('teacher').only('title', 'cover_url', 'video_url', 'profile', 'outline', 'teacher__name', 'teacher__avatar_url','teacher__positional_title', 'teacher__profile').filter(is_delete=False, id=course_id).first()
            return render(request, 'course/course_detail.html', locals())
        except Exception as e:
            logger.error('课程异常:{}'.format(e))
            raise Http404('此课程已经下架')