from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, ListAPIView
from rest_framework.decorators import api_view, permission_classes
from .serializers import StudioSerializer, CourseSerializer, ClassInstanceSerializer
from account.serializers import DroppedClassSerializer
from .models import Studio, Course, ClassInstance
from rest_framework.permissions import AllowAny, IsAuthenticated
from datetime import datetime
from rest_framework.response import Response
from account.models import DroppedClasses


class StudioListCreateView(ListCreateAPIView):
    serializer_class = StudioSerializer
    queryset = Studio.objects.all()

    def perform_create(self, serializer):
        pass  # specify how an instance should be created


class StudioDetailView(RetrieveAPIView):
    queryset = Studio.objects.all()
    serializer_class = StudioSerializer


class CourseListingView(ListCreateAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        studio_num = self.kwargs['studio_num']
        target_studio = Studio.objects.filter(id=studio_num)
        course_set = Course.objects.filter(studio__in=target_studio)

        return course_set


@api_view(['POST'])
@permission_classes([AllowAny])
def course_schedule_view(request):
    course_num = request.POST.get("course_id", -1)
    course = Course.objects.all().filter(id=course_num)
    if not course.exists():
        return Response({"message": "The course id is invalid"})
    course = course[0]
    classes = ClassInstance.objects.all().filter(course=course, time__gt=datetime.now())
    serializer = ClassInstanceSerializer(classes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def drop_course(request):
    if not request.user.site_user.subscription:
        return Response({"message": "You are not subscribed!"})
    course_num = request.POST.get("course_id", -1)
    site_user = request.user.site_user
    result = site_user.drop_course(course_num)
    if result:
        return Response({"message": "dropped successfully"})
    return Response({"message": "Drop failed, please check if the course id is valid, "
                                "and you're enrolling in the course."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_course(request):
    if not request.user.site_user.subscription:
        return Response({"message": "You are not subscribed!"})
    course_num = request.POST.get("course_id", -1)
    site_user = request.user.site_user
    result = site_user.enroll_course(course_num)
    if result:
        data = {"message": "enrolled successfully"}
    else:
        data = {"message": "enroll failed, please check if the course if is valid and has enough capacity and be"
                           " aware that double enrollment is not allowed."}
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def enrolled_courses(request):
    site_user = request.user.site_user
    classes = site_user.enrolled.all().order_by("time")
    serializer = ClassInstanceSerializer(classes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dropped_courses(request):
    site_user = request.user.site_user
    dropped = DroppedClasses.objects.all().filter(user=site_user).order_by("dropped__time")
    classes = [d.dropped for d in dropped]
    serializer = ClassInstanceSerializer(classes, many=True)
    return Response(serializer.data)
