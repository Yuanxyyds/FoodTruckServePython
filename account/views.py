from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes

from .serializers import UserTokenObtainPairSerializer, UserSerializer, \
    SubscriptionModelSerializer, SiteUserSerializer, PaymentSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import SubscriptionModel, Payment, SiteUser
from django.shortcuts import get_object_or_404
from datetime import datetime

# Create your views here.


class UserObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny, )
    serializer_class = UserTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = UserSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_view(request):
    serializer = UserSerializer(instance=request.user, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def site_user_view(request):
    serializer = SiteUserSerializer(instance=request.user.site_user, data=request.data, many=False, partial=True,
                                    context=request.POST)

    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['GET'])
def subscription_model_view(request):
    serializer = SubscriptionModelSerializer(SubscriptionModel.objects.all(), many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_view(request):
    sub_num = request.POST['subscription_id']
    result = request.user.site_user.subscribe(sub_num)
    if result:
        return Response({"message": "Successfully subscribed!"})
    return Response({"message": "Failed to subscribe! Please check your payment info and make sure the id of the "
                                "plan you're subscribing is valid"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unsubscribe_view(request):
    result = request.user.site_user.unsubscribe()
    if result:
        return Response({"message": "Successfully unsubscribed!"})
    return Response({"message": "Failed to unsubscribe! You are not subscribed!"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_view(request):
    payments = Payment.objects.all().filter(user=request.user.site_user)
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)
