from django.contrib import admin

from .models import *


class CourseDetailAdmin(admin.StackedInline):
    model = CourseDetail


class CourseChapterInline(admin.StackedInline):
    model = CourseChapter
    extra = 2


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
        CourseChapterInline
    ]
    # raw_id_fields = ('',)
    # readonly_fields = ('',)
    search_fields = ('course_name',)


@admin.register(CourseApply)
class CourseApplyAdmin(admin.ModelAdmin):
    '''
        Admin View for CourseApply
    '''
    list_display = ('apply_user', 'apply_course', 'apply_time')
    list_filter = ('apply_course',)
    # inlines = [
    #     Inline,
    # ]
    # raw_id_fields = ('',)
    readonly_fields = ('apply_time',)
    # search_fields = ('',)


admin.site.register(CateGory)
admin.site.register(CourseBanner)
