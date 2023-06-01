from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, TextChoices, ImageField
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    class UserType(TextChoices):
        CUSTOMER = "CUSTOMER"
        TRUCK_OWNER = "TRUCK_OWNER"

    avatar = ImageField(null=True, blank=True)
    address = CharField(null=True, blank=True, max_length=50)
    userType = CharField(choices=UserType.choices, blank=False, max_length=30)
    phone = PhoneNumberField(null=False, blank=False, unique=True)

