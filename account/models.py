from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.db.models import OneToOneField, CharField, ImageField,\
    DecimalField, ForeignKey, ManyToManyField, PositiveBigIntegerField,\
    PositiveIntegerField, BooleanField, DateTimeField, EmailField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MinValueValidator
from studio.models import ClassInstance
from django.utils import timezone
from dateutil.relativedelta import relativedelta

# Create your models here.
def only_int(num):
    if not num.isdigit():
        raise ValidationError(_('%(num)s is not an even number'),
                              params={'num': num}, )


class SubscriptionModel(models.Model):
    name = CharField(max_length=50, blank=False, default='')
    description = CharField(max_length=300, default='')
    type = BooleanField(default=True, choices=[(True, "Month"), (False, 'Year')])
    cost = DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'


class CardInfo(models.Model):
    number = CharField(max_length=16, validators=[only_int, MinLengthValidator(16)])
    cvv = CharField(max_length=3, validators=[only_int, MinLengthValidator(3)])
    is_credit = BooleanField(default=True)

    def __str__(self):
        return self.number


class Payment(models.Model):
    user = ForeignKey("SiteUser", on_delete=models.CASCADE, default=None, null=True)
    is_future = BooleanField(default=False)
    time = DateTimeField()
    amount = DecimalField(decimal_places=2, max_digits=20, validators=[MinValueValidator(0)])
    card_info = ForeignKey(CardInfo, on_delete=models.SET_NULL, null=True)


class SiteUser(models.Model):
    user = OneToOneField(DjangoUser, on_delete=models.CASCADE, default=None, null=True, related_name="site_user")
    subscription = ForeignKey(SubscriptionModel, on_delete=models.SET_NULL, null=True, blank=True)
    telephone = CharField(max_length=30, null=True, blank=True, default='')
    avatar = ImageField(null=True, blank=True)
    payment_info = ForeignKey(CardInfo, null=True, blank=True, on_delete=models.SET_NULL)
    enrolled = ManyToManyField('studio.ClassInstance', related_name='students')
    payment_due = DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    def set_payment_info(self, card_num, cvv, is_credit):
        if not self.payment_info:
            info = CardInfo()
        else:
            info = self.payment_info
        if card_num.isdigit() and len(card_num) == 16 and cvv.isdigit() and len(cvv) == 3:
            info.number = card_num
            info.cvv = cvv
            info.is_credit = is_credit == "yes"
            info.save()
            self.payment_info = info
            self.save()
            return True
        return False

    def make_payment(self):
        if self.subscription and self.payment_info:
            payment = Payment.objects.all().filter(is_future=True, user=self)
            if payment.exists():
                payment = payment[0]
                payment.amount = self.subscription.cost
                payment.save()
                if payment.time > timezone.now():
                    return
                payment.is_future = False
                payment.save()
            elif not self.payment_due or timezone.now() > self.payment_due:
                payment = Payment()
                payment.card_info = self.payment_info
                payment.amount = self.subscription.cost
                payment.time = timezone.now()
                payment.user = self
                payment.save()
            future = Payment()
            future.card_info = self.payment_info
            future.amount = self.subscription.cost
            delta = relativedelta(months=1) if self.subscription.type else relativedelta(years=1)
            future.time = timezone.now() + delta
            future.user = self
            future.is_future = True
            future.save()
            self.payment_due = future.time

    def subscribe(self, pk):
        s = SubscriptionModel.objects.all().filter(pk=pk)
        if s.exists() and self.payment_info:
            self.subscription = s[0]
            if (not self.payment_due) or timezone.now() > self.payment_due:
                self.make_payment()
            else:
                future_payment = Payment()
                future_payment.time = timezone.now() + \
                                      relativedelta(months=1) if self.subscription.type else relativedelta(years=1)
                future_payment.amount = self.subscription.cost
                future_payment.user = self
                future_payment.is_future = True
                future_payment.card_info = self.payment_info
                future_payment.save()
            self.save()
            return True
        return False

    def unsubscribe(self):
        if not self.subscription:
            return False
        self.subscription = None
        payment = Payment.objects.all().filter(is_future=True, user=self)
        if payment.exists():
            payment = payment[0]
            invalid_classes = self.enrolled.all().filter(time__gt=payment.time)
            for i in invalid_classes:
                self.enrolled.remove(i)
            payment.delete()
        self.save()
        return True

    def add_payment_info(self, is_credit, number, cvv):
        card = CardInfo()
        card.is_credit = is_credit
        card.number = number
        card.cvv = cvv
        card.save()
        self.payment_info = card
        self.save()

    def enroll_course(self, pk):
        if not self.subscription:
            return False
        course = ClassInstance.objects.all().filter(pk=pk, time__gt=timezone.now())
        if course.exists():
            course = course[0]
            # Enrolled course cannot be enrolled again
            if course.canceled or course.students.all().count() >= course.capacity or\
                    course.students.filter(pk=self.pk).exists():
                return False
            if course.students.count() >= course.capacity:
                return False
            dropped = DroppedClasses.objects.all().filter(user=self, dropped=course)
            if dropped.exists():
                dropped[0].delete()
            self.enrolled.add(course)
            self.save()
            return True
        return False

    def drop_course(self, pk):
        if not self.subscription:
            return False
        course = ClassInstance.objects.all().filter(pk=pk, time__gt=timezone.now())
        if course.exists():
            course = course[0]
            if not course.students.filter(pk=self.pk).exists():
                return False
            self.enrolled.remove(course)
            drop_record = DroppedClasses()
            drop_record.user = self
            drop_record.dropped = course
            drop_record.save()
            self.save()
            return True
        return False


class DroppedClasses(models.Model):
    user = ForeignKey(SiteUser, on_delete=models.CASCADE)
    dropped = ForeignKey("studio.ClassInstance", on_delete=models.CASCADE)
