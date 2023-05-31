from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from .models import SiteUser, SubscriptionModel, Payment, CardInfo, DroppedClasses
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(UserTokenObtainPairSerializer, cls).get_token(user)

        token['username'] = user.username
        return token


class SiteUserSerializer(serializers.ModelSerializer):
    telephone = serializers.CharField(required=False)
    user = serializers.SerializerMethodField()
    subscription = serializers.SerializerMethodField()
    enrolled = serializers.SerializerMethodField()
    payment_info = serializers.SerializerMethodField()

    class Meta:
        model = SiteUser
        fields = ['user', 'subscription', 'telephone', 'enrolled', 'payment_info', 'payment_due', 'avatar']

    def get_user(self, obj):
        return obj.user.username

    def get_subscription(self, obj):
        return obj.subscription.name

    def get_enrolled(self, obj):
        cs = obj.enrolled.all()
        if cs.count() == 0:
            return '[]'
        s = '[' + str(cs[0].pk)

        for i in range(1, len(cs)):
            s += ', ' + str(cs[i].pk)
        s += ']'
        return s

    def get_payment_info(self, obj):
        info = obj.payment_info
        return {
            "Card Number": info.number,
            "CVV": info.cvv,
            "Type": "Credit" if info.is_credit else "Debit"
        }

    def validate_telephone(self, value):
        if value.isdigit():
            return value
        raise serializers.ValidationError("Telephone must be numbers!")

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if "card_number" in self.context and "cvv" in self.context and "is_credit" in self.context:
            instance.set_payment_info(self.context['card_number'], self.context['cvv'],
                                      self.context['is_credit'])
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password2']

    def validate(self, attrs):
        if 'password' in attrs and 'password2' in attrs:
            if attrs['password'] != attrs['password2']:
                raise serializers.ValidationError({"password": "password must match"})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()

        site_user = SiteUser(
            user=user,
        )
        site_user.save()
        return user

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            instance.save()
        return instance


class SubscriptionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        fields = ['id', 'name', 'description', 'type', 'cost']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'time', 'amount', 'card_info', 'is_future']


class DroppedClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroppedClasses
        fields = ["dropped", "user"]
