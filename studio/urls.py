from django.urls import path
from .views import StudioListCreateView, StudioDetailView, CourseListingView,\
    course_schedule_view, enrolled_courses, enroll_course, drop_course, dropped_courses

app_name = "Studio"

urlpatterns = [
    path('list/', StudioListCreateView.as_view()),
    path('<int:pk>/detail/', StudioDetailView.as_view()),
    path('<int:studio_num>/courses/', CourseListingView.as_view()),
    path('course/schedule/', course_schedule_view),
    path('user/enrolled/', enrolled_courses, name='enrolled_courses'),
    path('user/enroll/', enroll_course, name="enroll"),
    path('user/drop/', drop_course, name='drop'),
    path('user/dropped/', dropped_courses, name='dropped_courses'),
]
