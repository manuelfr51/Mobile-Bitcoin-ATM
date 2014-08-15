from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse

from phonenumber_field.modelfields import PhoneNumberField

from utils import get_client_ip
from countries import ALL_COUNTRIES

AbstractUser._meta.get_field_by_name('username')[0].max_length = 100
AbstractUser._meta.get_field('username').validators[0].limit_value = 100


class AuthUser(AbstractUser):
    """
    Right now this is just merchants but it can support cashiers, shoppers,
    owners with multiple merchants and all types of things in the future.

    http://qr.ae/svQjw
    """
    full_name = models.CharField(max_length=60, blank=True,
            null=True, db_index=True)
    phone_num = PhoneNumberField(blank=True, null=True, db_index=True)
    phone_num_country = models.CharField(
        max_length=256, blank=True, null=True, db_index=True)

    def get_merchant(self):
        return self.merchant_set.last()

    def get_login_uri(self):
        return '%s?e=%s' % (reverse('login_request'), self.email)


class LoggedLogin(models.Model):
    login_at = models.DateTimeField(auto_now_add=True, db_index=True)
    auth_user = models.ForeignKey(AuthUser, blank=False, null=False)
    ip_address = models.IPAddressField(null=False, blank=False, db_index=True)
    user_agent = models.CharField(max_length=1024, blank=True, db_index=True)

    def __str__(self):
        return '%s: %s' % (self.id, self.ip_address)

    @classmethod
    def record_login(cls, request):
        return cls.objects.create(
                auth_user=request.user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                )


class FutureShopper(models.Model):
    """
    Customer that signed up to be notified when merchants are in their area
    """
    email = models.EmailField(blank=False, null=False, db_index=True)
    city = models.CharField(max_length=256, blank=True, null=True, db_index=True)
    country = models.CharField(max_length=256, blank=False, null=False, db_index=True, choices=ALL_COUNTRIES)
    intention = models.CharField(max_length=256, blank=True, null=True, db_index=True)
    message = models.CharField(max_length=5000, blank=True, null=True)

    def __str__(self):
        return '%s: %s' % (self.id, self.email)
