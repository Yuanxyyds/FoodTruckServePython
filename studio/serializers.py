from rest_framework import serializers
from .models import Studio, Course, ClassInstance


class StudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Studio
        fields = ['id', 'name', 'address', 'latitude', 'longitude', 'postal', 'phone']


class CourseSerializer(serializers.ModelSerializer):
    studio = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'studio', 'name', 'start_date', 'end_date', 'description',
                  'coach', 'capacity']

    def get_studio(self, obj):
        return {"id": obj.studio.id, "name": obj.studio.name}


class ClassInstanceSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()

    class Meta:
        model = ClassInstance
        fields = ['id', 'time', 'course', 'canceled', 'capacity', 'students']

    def get_students(self, obj):
        return obj.students.all().count()

