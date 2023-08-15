from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models.query import QuerySet
from licenses.models import Client, License
import pytz
from licenses.notifications import EmailNotification

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

def expiration_date_that_gets_notification(expiration_date:datetime) -> bool:
    today:datetime = datetime.utcnow().replace(tzinfo=pytz.utc)
    time_to_expire:timedelta = expiration_date - today
    if time_to_expire.days <= DAYS_IN_A_WEEK: # The client has licenses which expire within a week
        return True

    months_difference:timedelta = diff_month(expiration_date, today)
    if months_difference == 0 and today.weekday() in DAYS_TO_SEND_EMAILS_EXPIRING_IN_A_MONTH: #The client has licenses which expire within a month and today is monday
        return True

    if months_difference == NUMBER_OF_MONTHS_TO_CHECK_LICENSE_EXPIRATION and expiration_date.day == today.day: #The client has licenses which expire in exactly 4 months
        return True

    return False

def should_receive_notification(client_id:int) -> bool:
    licenses_expiration_dates = client_licenses_that_will_expire_soon(client_id).values_list(
        'expiration_datetime', flat=True
    ).distinct()

    for expiration_date in licenses_expiration_dates:
        if expiration_date_that_gets_notification(expiration_date):
            return True

    return False

class LicenseExpirationNotification(EmailNotification):
    template_path:str = 'licenses/license_notification.html'

def notify_license_expiration(client_id:int) -> None:
    licenses_that_will_expire_soon:QuerySet[License] = client_licenses_that_will_expire_soon(client_id)
    licenses_that_need_notification:typing.List[License] = []
    for license in licenses_that_will_expire_soon:
        if expiration_date_that_gets_notification(license.expiration_datetime):
            licenses_that_need_notification.append(license)

    client_object = Client.objects.get(id=client_id)
    LicenseExpirationNotification.send_notification(
        [client_object.admin_poc.email],
        {
            'licenses': licenses_that_will_expire_soon,
            'client': client_object
        },
        subject=f"{client_object} has expiring licenses!"
    )
