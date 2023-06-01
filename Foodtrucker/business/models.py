from django.db import models
from django.db.models import CharField, BooleanField, ImageField, TextField, \
    ForeignKey, FloatField, TextChoices, IntegerField
from user.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Shop(models.Model):
    owner = ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    icon = ImageField(null=True, blank=True)
    opened = BooleanField(default=False, blank=False)
    description = TextField(blank=True)
    area = CharField(blank=False, max_length=30)
    location = CharField(blank=False, max_length=50)

    def open(self):
        self.opened = True
        self.save()

    def close(self):
        self.opened = False
        self.save()


class Item(models.Model):
    shop = ForeignKey(Shop, on_delete=models.CASCADE, default=None, null=True)
    name = CharField(max_length=20, blank=False)
    icon = ImageField(null=True, blank=True)
    availability = BooleanField(default=True, blank=False, null=True)
    price = FloatField(validators=[MinValueValidator(0)])

    def enable(self):
        self.availability = True
        self.save()

    def disable(self):
        self.availability = False
        self.save()


class Order(models.Model):
    class OrderStatus(TextChoices):
        COMPLETED = "completed"
        OPENED = "opened"
        CANCELED = "canceled"

    status = CharField(choices=OrderStatus.choices, max_length=30)
    shop = ForeignKey(Shop, on_delete=models.SET_NULL, blank=False, null=True)
    customer = ForeignKey(User, on_delete=models.SET_NULL, blank=False,
                          null=True)

    ''' Compute the total price of the order
    '''
    def price(self):
        cartItems = CartItem.objects.all().filter(order=self)
        s = 0
        if cartItems.exists():
            for ci in cartItems:
                s += (ci.item.price * ci.quantity)
        return s * 1.13

    def complete(self):
        if self.status == Order.OrderStatus.OPENED:
            self.status = Order.OrderStatus.COMPLETED
            self.save()

    def cancel(self):
        if self.status == Order.OrderStatus.OPENED:
            self.status = Order.OrderStatus.CANCELED
            self.save()


class CartItem(models.Model):
    order = ForeignKey(Order, on_delete=models.CASCADE, blank=False, null=True)
    item = ForeignKey(Item, on_delete=models.SET_NULL, blank=False, null=True)
    quantity = IntegerField(blank=False, validators=[MinValueValidator(1)])

