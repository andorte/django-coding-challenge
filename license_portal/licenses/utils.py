from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models.query import QuerySet
from licenses.models import Client, License
import pytz


DAYS_IN_A_WEEK:int = 7
DAYS_TO_SEND_EMAILS_EXPIRING_IN_A_MONTH:int = [0] # Monday
NUMBER_OF_MONTHS_TO_CHECK_LICENSE_EXPIRATION:int = 4

def diff_month(d1:datetime, d2:datetime) -> int:
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def licenses_that_will_expire_soon() -> QuerySet[License]:
    today:datetime = datetime.utcnow().replace(tzinfo=pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    max_date_that_should_be_notified:datetime = today+relativedelta(months=NUMBER_OF_MONTHS_TO_CHECK_LICENSE_EXPIRATION)
    return License.objects.filter(
        expiration_datetime__gte=today,
        expiration_datetime__lte=max_date_that_should_be_notified
    )

def client_licenses_that_will_expire_soon(client:Client) -> QuerySet[License]:
    return licenses_that_will_expire_soon().filter(
        client = client
    )

def should_receive_notification(client:Client) -> bool:
    today:datetime = datetime.utcnow().replace(tzinfo=pytz.utc)

    licenses_expiration_dates = client_licenses_that_will_expire_soon(client).values_list(
        'expiration_datetime', flat=True
    ).distinct()

    for expiration_date in licenses_expiration_dates:
        time_to_expire = expiration_date - today
        if time_to_expire.days <= DAYS_IN_A_WEEK: # The client has licenses which expire within a week
            return True

        months_difference:relativedelta = diff_month(expiration_date, today)
        if months_difference == 0 and today.weekday() in DAYS_TO_SEND_EMAILS_EXPIRING_IN_A_MONTH: #The client has licenses which expire within a month and today is monday
            return True

        if months_difference == NUMBER_OF_MONTHS_TO_CHECK_LICENSE_EXPIRATION and expiration_date.day == today.day: #The client has licenses which expire in exactly 4 months
            return True

    return False

def notify_license_expiration(client:Client) -> None:
    #TODO notify client
    print(f"Notifying {client}")