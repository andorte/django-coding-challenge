from django.shortcuts import render
from licenses.models import Client, License
from datetime import datetime
import pytz

DAYS_IN_A_WEEK:int = 7
DAYS_TO_SEND_EMAILS_EXPIRING_IN_A_MONTH:int = [0] # Monday

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def should_receive_notification(client:Client)->bool:
    today = datetime.utcnow().replace(tzinfo=pytz.utc)

    licenses_expiration_dates = License.objects.filter(
        client=client,
        expiration_datetime__gte=today
    ).values_list(
        'expiration_datetime', flat=True
    ).distinct()

    for expiration_date in licenses_expiration_dates:
        time_to_expire = expiration_date - today
        if time_to_expire.days <= DAYS_IN_A_WEEK: # The client has licenses which expire within a week
            return True

        months_difference = diff_month(expiration_date, today)
        if months_difference == 0 and today.weekday() in DAYS_TO_SEND_EMAILS_EXPIRING_IN_A_MONTH: #The client has licenses which expire within a month and today is monday
            return True

        if months_difference == 4 and expiration_date.day == today.day: #The client has licenses which expire in exactly 4 months
            return True

    return False
