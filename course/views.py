from user.auth import CheckUserWrap

from django.http import Http404, JsonResponse
from django.views.generic import DetailView, FormView, ListView, View
from dss.Mixin import (FormJsonResponseMixin, JsonResponseMixin,
                       MultipleJsonResponseMixin)
from dss.Serializer import serializer

from .models import *


# Create your views here.
class CourseListView(MultipleJsonResponseMixin, ListView):
    """docstring for CourseListView"""
    model = Course
    paginate_by = 15
    foreign = True
    datetime_format = 'string'

    def get_queryset(self):
        kwargs = dict()
        category = self.request.GET.get('category', None)

        if category:
            try:
                category = int(category)
                kwargs['course_cate_id'] = category
            except:
                pass
        queryset = super(CourseListView, self).get_queryset()
        queryset = queryset.filter(**kwargs)
        return queryset


class CourseIndexView(JsonResponseMixin, View):

    exclude_attr = ('course_cate_id', 'course_cate')
    def get(self, request, *args, **kwargs):
        result = []
        all_category = CateGory.objects.all()
        for i in all_category:
            result.append({
                'category': i,
                'course_list': i.course_set.all()[:6]
            })

        return self.render_to_response({'index': result})


class CourseDetailView(JsonResponseMixin, DetailView, CheckUserWrap):
    model = CourseDetail
    pk_url_kwarg = 'course_id'
    
    def get_context_data(self, **kwargs):
        if not self.wrap_check_token_result():
            self.user = None
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        context['is_apply'] = CourseApply.objects.filter(apply_user=self.user, apply_course=self.object.course).exists()
        return context


class CourseChapterView(JsonResponseMixin, DetailView, CheckUserWrap):
    model = Course
    pk_url_kwarg = 'course_id'

    def get_context_data(self, **kwargs):
        if not self.wrap_check_token_result():
            self.user = None
        context = super(CourseChapterView, self).get_context_data(**kwargs)
        context['is_apply'] = CourseApply.objects.filter(apply_user=self.user, apply_course=self.object).exists()
        context['chapter_list'] = serializer(
            [{'chapter': i, 'videos': serializer(i.coursechaptervideo_set.all(), exclude_attr=('chapter', ))} for i in self.object.coursechapter_set.all()],
            exclude_attr=('course', ))
        return context


class ApplyCourseView(JsonResponseMixin, View, CheckUserWrap):
    model = CourseApply

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_token_result():
            return self.render_to_response({'msg': self.msg})

        course_id = kwargs.get('course_id')
        try:
            course = Course.objects.get(id=course_id)
        except:
            raise Http404()

        if self.model.objects.filter(apply_user=self.user, apply_course=course).exists():
            return self.render_to_response({'msg': '已报名'})

        self.model.objects.create(apply_user=self.user, apply_course=course)
        return self.render_to_response({'msg': 'ok'})


class CourseBannerView(JsonResponseMixin, View):
    model = CourseBanner
    exclude_attr = ('banner_course',)
    
    def get(self, request, *args, **kwargs):
        count = self.request.GET.get('count', 4)
        try:
            count = int(count)
        except:
            count = 4

        qr = self.model.objects.all()[:count]
        return self.render_to_response(qr)


def all_category_view(request):
    all_cate = CateGory.objects.all()
    return JsonResponse({'lists': serializer(all_cate)})