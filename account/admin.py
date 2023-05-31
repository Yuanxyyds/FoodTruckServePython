from django.contrib import admin
from .models import SiteUser, SubscriptionModel, CardInfo, Payment, DroppedClasses
from nested_admin.nested import NestedModelAdmin, NestedTabularInline, NestedStackedInline


class PaymentInline(NestedTabularInline):
    model = Payment
    extra = 0
    can_delete = False
    readonly_fields = ['time', 'amount', 'card_info', 'is_future']
    verbose_name = 'Payment'
    verbose_name_plural = 'Payments'

    def __str__(self):
        return "Payment"


def string_site_user(obj):
    return str(obj)


class DroppedClassInline(NestedTabularInline):
    model = DroppedClasses
    extra = 0
    can_delete = False
    readonly_fields = ['course_id', 'course_name', 'time']
    exclude = ['dropped']
    verbose_name = "Class Dropped"
    verbose_name_plural = "Classes Dropped"

    def course_id(self, obj):
        return obj.dropped.pk

    def course_name(self, obj):
        return obj.dropped.name

    def time(self, obj):
        return obj.dropped.time


class SiteUserAdmin(NestedModelAdmin):
    model = SiteUser
    can_delete = False
    verbose_name_plural = "site user"
    exclude = ['enrolled']
    readonly_fields = ['enrolled_class_IDs']
    list_display = ["__str__"]
    list_display_links = ["__str__"]
    inlines = [PaymentInline, DroppedClassInline]

    def enrolled_class_IDs(self, obj):
        cs = obj.enrolled.all()
        if cs.count() == 0:
            return '[]'
        s = '[' + str(cs[0].pk)

        for i in range(1, len(cs)):
            s += ', ' + str(cs[i].pk)
        s += ']'
        return s


class SubscriptionModelAdmin(admin.ModelAdmin):
    list_display = ["name", 'type', "cost"]

    def active(self, obj):
        return obj.is_active == 1

    active.boolean = True


# Register your models here.
admin.site.register(SiteUser, SiteUserAdmin)
admin.site.register(SubscriptionModel, SubscriptionModelAdmin)


@admin.register(CardInfo)
class CardInfoAdmin(admin.ModelAdmin):
    inlines = []


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    inlines = []
