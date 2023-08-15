""" Data model for licenses application
"""
import enum

from datetime import timedelta, datetime
from typing import Tuple, List

from django.contrib.auth.models import User
from django.db import models

LICENSE_EXPIRATION_DELTA = timedelta(days=90)


class ChoiceEnum(enum.Enum):
    """Enum for choices in a choices field"""
    @classmethod
    def get_choices(cls) -> List[Tuple[str, int]]:
        return [(a.name, a.value) for a in cls]


# The original get_choices is using the name as key. This one works with django admin.
class ValueNameChoiceEnum(ChoiceEnum):
    @classmethod
    def get_choices(cls) -> tuple:
        return tuple((i.value, i.name) for i in cls)

class Package(ValueNameChoiceEnum):
    """A Package accessible to a client with a valid license"""
    javascript_sdk = 0
    ios_sdk = 1
    android_sdk = 2


class LicenseType(ValueNameChoiceEnum):
    """A license type"""
    production = 0
    evaluation = 1


def get_default_license_expiration() -> datetime:
    """Get the default expiration datetime"""
    return datetime.utcnow() + LICENSE_EXPIRATION_DELTA


class License(models.Model):
    """ Data model for a client license allowing access to a package
    """
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    package = models.PositiveSmallIntegerField(choices=Package.get_choices())
    license_type = models.PositiveSmallIntegerField(choices=LicenseType.get_choices())

    created_datetime = models.DateTimeField(auto_now=True)
    expiration_datetime = models.DateTimeField(default=get_default_license_expiration)


class Client(models.Model):
    """ A client who holds licenses to packages
    """
    client_name = models.CharField(max_length=120, unique=True)
    poc_contact_name = models.CharField(max_length=120)
    poc_contact_email = models.EmailField()

    admin_poc = models.ForeignKey(User, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.client_name}"

class NotificationSummary(models.Model):
    sending_date = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(Client, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE)
    admin_poc = models.ForeignKey(User, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE)
    quantity_of_notificated_licenses = models.PositiveSmallIntegerField()
