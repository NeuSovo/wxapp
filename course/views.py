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


class CourseDetailView(JsonResponseMixin, DetailView):
    model = CourseDetail
    pk_url_kwarg = 'course_id'


class CourseChapterView(JsonResponseMixin, DetailView):
    model = Course
    pk_url_kwarg = 'course_id'

    def get_context_data(self, **kwargs):
        context = super(CourseChapterView, self).get_context_data(**kwargs)
        context['chapter_list'] = serializer(
            [{'chapter': i, 'videos': i.coursechaptervideo_set.all()} for i in self.object.coursechapter_set.all()],
            exclude_attr=('course', ))
        return context

