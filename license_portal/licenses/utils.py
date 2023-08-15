from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models.query import QuerySet
from django.db.models import Q
from licenses.models import Client, License, NotificationSummary
import pytz
from licenses.notifications import EmailNotification

DAYS_IN_A_WEEK:int = 7
DAYS_TO_SEND_EMAILS_EXPIRING_IN_A_MONTH:int = [0] # Monday
NUMBER_OF_MONTHS_TO_CHECK_LICENSE_EXPIRATION:int = 4

def licenses_that_needs_notification() -> QuerySet[License]:
    today:datetime = datetime.utcnow().replace(tzinfo=pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    expiring_licenses_notification_filter = (
        # The license expire within a week
        Q(expiration_datetime__gte=today) & Q(expiration_datetime__lte=today+relativedelta(days=DAYS_IN_A_WEEK+1))
    ) | (
        # The licenses expire in exactly 4 months
        Q(expiration_datetime__gte=today+relativedelta(months=NUMBER_OF_MONTHS_TO_CHECK_LICENSE_EXPIRATION)) &
        Q(expiration_datetime__lt=today+relativedelta(months=NUMBER_OF_MONTHS_TO_CHECK_LICENSE_EXPIRATION, days=1))
    )

    # The license expire within a month and today is monday
    if today.weekday() in DAYS_TO_SEND_EMAILS_EXPIRING_IN_A_MONTH:
        expiring_licenses_notification_filter = expiring_licenses_notification_filter | (
            Q(expiration_datetime__lt=today+relativedelta(months=1)) &
            Q(expiration_datetime__gt=today)
        )

    return License.objects.filter(expiring_licenses_notification_filter)

def client_licenses_that_needs_notification(client_id:int) -> QuerySet[License]:
    return licenses_that_needs_notification().filter(client = client_id)

def should_receive_notification(client_id:int) -> bool:
    return client_licenses_that_needs_notification(client_id).exists()

class LicenseExpirationNotification(EmailNotification):
    template_path:str = 'licenses/license_notification.html'

def notify_license_expiration(client_id:int) -> None:
    licenses_that_needs_notification:QuerySet[License] = client_licenses_that_needs_notification(client_id)

    client_object = Client.objects.get(id=client_id)
    LicenseExpirationNotification.send_notification(
        [client_object.admin_poc.email],
        {
            'licenses': licenses_that_needs_notification,
            'client': client_object
        },
        subject=f"{client_object} has expiring licenses!"
    )

    NotificationSummary.objects.create(
        client=client_object,
        admin_poc=client_object.admin_poc,
        quantity_of_notificated_licenses = licenses_that_needs_notification.__len__()
    )
