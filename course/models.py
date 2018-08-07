from django.db import models
from simditor.fields import RichTextField
# Create your models here.

from user.models import User

class CateGory(models.Model):

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类"

    def __str__(self):
        return self.category_name
    
    category_name = models.CharField(max_length=50, verbose_name='分类名字')


class Course(models.Model):

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = "课程"

    def __str__(self):
        return self.course_name

    course_name = models.CharField(max_length=100, verbose_name='课程名字')
    course_cate = models.ForeignKey(CateGory, on_delete=models.SET_NULL, null=True, verbose_name='分类')
    course_cover = models.ImageField(upload_to="coursecover", verbose_name='课程封面', default='none', null=True)
    add_time = models.DateTimeField(auto_now_add=True)


class CourseDetail(models.Model):

    class Meta:
        verbose_name = "课程详细"
        verbose_name_plural = "课程详细"

    def __str__(self):
        return str(self.course)

    course = models.OneToOneField(Course, on_delete=models.CASCADE, primary_key=True)
    detail = RichTextField(verbose_name='介绍', default='无')
    

class CourseChapter(models.Model):

    class Meta:
        verbose_name = "章节视频"
        verbose_name_plural = "章节视频"

    def __str__(self):
        return str(self.course) + ':' + self.chapter_title

    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')
    chapter_title = models.CharField(max_length=50, verbose_name='章节标题')


class CourseChapterVideo(models.Model):

    class Meta:
        verbose_name = "视频"
        verbose_name_plural = "视频"

    chapter = models.ForeignKey(CourseChapter, on_delete=models.CASCADE)
    video_title = models.CharField(max_length=50, verbose_name='视频标题')
    video_url = models.URLField(verbose_name='腾讯视频url地址')
    vid = models.CharField(max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        try:
            self.vid = self.video_url.split('/')[-1].split('.')[0]
        except:
            pass
        super().save(*args, **kwargs)


class CourseBanner(models.Model):

    class Meta:
        verbose_name = "课程轮播图"
        verbose_name_plural = "课程轮播图"

    def __str__(self):
        return self.banner_title or '空标题'

    banner_title = models.CharField(max_length=50, verbose_name='轮播标题', null=True, blank=True)
    banner_img = models.ImageField(upload_to="coursebanner", verbose_name='轮播图', default='none', null=True)
    banner_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联的课程', help_text='点击跳转到于此关联的课程，可以填空')


class CourseApply(models.Model):

    class Meta:
        verbose_name = "课程报名表"
        verbose_name_plural = "课程报名表"

    def __str__(self):
        return str(self.apply_course) + ':' + str(self.apply_user)

    apply_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='报名用户')
    apply_course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='报名课程')
    apply_time = models.DateTimeField(auto_now_add=True, verbose_name='报名时间')
