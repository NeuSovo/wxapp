from django.contrib import admin
from .models import *

class CourseDetailAdmin(admin.StackedInline):
    model = CourseDetail


class CourseChapterVideoAdmin(admin.StackedInline):
    extra = 1
    model = CourseChapterVideo
    readonly_fields = ('vid',)


@admin.register(CourseChapter)
class CourseChapterAdmin(admin.ModelAdmin):
    '''
        Admin View for CourseChapter
    '''
    list_display = ('course', 'chapter_title')
    list_filter = ('course',)
    inlines = [
        CourseChapterVideoAdmin,
    ]
    # raw_id_fields = ('',)
    # readonly_fields = ('',)
    # search_fields = ('',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    '''
        Admin View for 
    '''
    list_display = ('course_name', 'course_cate', )
    list_filter = ('course_cate',)
    inlines = [
        CourseDetailAdmin,
    ]
    # raw_id_fields = ('',)
    # readonly_fields = ('',)
    search_fields = ('course_name',)


admin.site.register(CateGory)