from django.db import models
from simditor.fields import RichTextField
# Create your models here.

class CateGory(models.Model):

    class Meta:
        verbose_name = "CateGory"
        verbose_name_plural = "CateGorys"

    def __str__(self):
        return self.category_name
    
    category_name = models.CharField(max_length=50)


class Course(models.Model):

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.course_name

    course_name = models.CharField(max_length=100, verbose_name='课程名字')
    course_cate = models.ForeignKey(CateGory, on_delete=models.SET_NULL, null=True, verbose_name='分类')
    course_cover = models.ImageField(upload_to="coursecover", verbose_name='课程封面', default='none', null=True)


class CourseDetail(models.Model):

    class Meta:
        verbose_name = "CourseDetail"
        verbose_name_plural = "CourseDetails"

    def __str__(self):
        return str(self.course)

    course = models.OneToOneField(Course, on_delete=models.CASCADE, primary_key=True)
    detail = RichTextField(verbose_name='介绍', default='无')
    
    