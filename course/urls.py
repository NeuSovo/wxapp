from django.urls import path
from .views import  *

urlpatterns = [
    path('', CourseListView.as_view()),
    path('index', CourseIndexView.as_view()),
    path('detail/<int:course_id>', CourseDetailView.as_view()),
    path('chapter/<int:course_id>', CourseChapterView.as_view()),
    path('apply/<int:course_id>', ApplyCourseView.as_view()),
    path('category', all_category_view)
]