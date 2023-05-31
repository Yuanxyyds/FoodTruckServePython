from django.contrib import admin
from .models import Studio, ClassInstance, Course, CourseKeyword, StudioImage, CourseSession
from account.models import SiteUser
from nested_admin.nested import NestedStackedInline, NestedTabularInline, NestedModelAdmin
from django.contrib.auth.models import User


class StudioImageInline(NestedStackedInline):
    model = StudioImage
    can_delete = True
    extra = 0


class CourseKeywordInline(NestedTabularInline):
    model = CourseKeyword
    can_delete = True
    extra = 0
    classes = ['collapse']


class ClassInstanceInline(NestedTabularInline):
    model = ClassInstance
    can_delete = True
    extra = 0
    classes = ['collapse']
    readonly_fields = ['capacity', 'enrolled']

    def enrolled(self, obj):
        return obj.students.all().count()


class CourseTimeInline(NestedTabularInline):
    model = CourseSession
    can_delete = True
    extra = 0
    classes = ['collapse']


class CourseInline(NestedStackedInline):
    inlines = [CourseKeywordInline, CourseTimeInline, ClassInstanceInline]
    model = Course
    can_delete = True
    extra = 0
    classes = ['collapse']


@admin.register(Studio)
class StudioAdmin(NestedModelAdmin):
    inlines = [CourseInline, StudioImageInline]
