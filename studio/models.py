from django.db import models
from django.db.models import ForeignKey, CharField, DecimalField, ImageField, \
    PositiveIntegerField, DateTimeField, BooleanField, ManyToManyField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from django.core.validators import MaxValueValidator, MinValueValidator


class Studio(models.Model):
    name = CharField(max_length=50)
    address = CharField(max_length=200)
    latitude = DecimalField(max_digits=9, decimal_places=6)
    longitude = DecimalField(max_digits=9, decimal_places=6)
    postal = CharField(max_length=10)
    phone = CharField(max_length=20)

    def __str__(self):
        return self.name


class StudioImage(models.Model):
    studio = ForeignKey(Studio, on_delete=models.CASCADE)
    image = ImageField()


class Course(models.Model):
    studio = ForeignKey(Studio, on_delete=models.CASCADE)
    start_date = DateTimeField(null=True, blank=False)
    end_date = DateTimeField(null=True, blank=False)
    name = CharField(max_length=50)
    description = CharField(max_length=300)
    coach = CharField(max_length=50)
    capacity = PositiveIntegerField(default=50)


class CourseSession(models.Model):
    session = CharField(default="", max_length=30)
    course = ForeignKey(Course, on_delete=models.CASCADE)
    day = PositiveIntegerField(blank=False, null=False, validators=[MaxValueValidator(6), MinValueValidator(0)])
    hour = PositiveIntegerField(blank=False, null=False, validators=[MaxValueValidator(23), MinValueValidator(0)])
    minute = PositiveIntegerField(blank=False, null=False, validators=[MaxValueValidator(59), MinValueValidator(0)])

    def __str__(self):
        return self.session

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['day', 'hour'], name='course_time'
            )
        ]


class CourseKeyword(models.Model):
    course = ForeignKey(Course, on_delete=models.CASCADE)
    word = CharField(max_length=20)


class ClassInstance(models.Model):
    time = DateTimeField()
    canceled = BooleanField(default=False)
    course = ForeignKey(Course, on_delete=models.CASCADE)
    capacity = PositiveIntegerField(default=50)

    def __str__(self):
        return str(self.id)


@receiver(pre_save, sender=CourseSession)
def instantiate_class_instances(sender, instance, **kwargs):
    # Clear existing class instances and update with new ones
    ClassInstance.objects.filter(course=instance.course).delete()

    date = instance.course.start_date + timedelta(days=instance.day) + timedelta(hours=instance.hour) + \
        timedelta(minutes=instance.minute)

    while date < instance.course.end_date:
        class_instance = ClassInstance(time=date, course=instance.course, capacity=instance.course.capacity)
        class_instance.save()
        date += timedelta(days=7)
