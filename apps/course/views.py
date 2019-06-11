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
    # 返回所有课程信息，以及教师表的信息
    :param request:
    :return:
    """
    courses = models.Course.objects.select_related('teacher').only('title', 'cover_url', 'teacher__name', 'teacher__positional_title').filter(is_delete=False)
    return render(request, 'course/course.html', locals())


class CourseDetailView(View):
    """
    # 课程详情，播放
    /course/<int:course_id>/
    course_id是课程唯一值
    查询唯一的课程，返回
    """
    def get(self, request, course_id):
        try:
            course = models.Course.objects.select_related('teacher').only('title', 'cover_url', 'video_url', 'profile', 'outline', 'teacher__name', 'teacher__avatar_url','teacher__positional_title', 'teacher__profile').filter(is_delete=False, id=course_id).first()
            return render(request, 'course/course_detail.html', locals())
        except Exception as e:
            logger.error('课程异常:{}'.format(e))
            raise Http404('此课程已经下架')