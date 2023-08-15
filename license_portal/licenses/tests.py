from django.test import TestCase
from licenses.utils import should_receive_notification, DAYS_IN_A_WEEK, DAYS_TO_SEND_EMAILS_EXPIRING_IN_A_MONTH
from licenses.models import Client, License
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
import pytz
import time_machine

def create_license (client:Client, expiration_date:datetime) -> License:
    return License.objects.create(
        expiration_datetime = expiration_date.replace(tzinfo=pytz.utc),
        package = 1,
        license_type = 1,
        client = client
    )

class NotificationBusinessLogicTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user:User = User.objects.create(username = "Automated Test Client")

    def get_client(self) -> Client:
        return Client.objects.create(admin_poc=self.user)

    def test_no_licenses(self):
        self.assertFalse(should_receive_notification(self.get_client()))
 
    def test_with_license_expiring_within_7_days(self):
        client:Client = self.get_client()
        create_license(client, (datetime.utcnow() + timedelta(days=DAYS_IN_A_WEEK+1)))
        self.assertTrue(should_receive_notification(client))

    def test_with_license_expiring_within_6_days(self):
        client:Client = self.get_client()
        create_license(client, (datetime.utcnow() + timedelta(days=DAYS_IN_A_WEEK)))
        self.assertTrue(should_receive_notification(client))

    def test_with_license_expiring_within_a_month_and_is_monday(self):
        client:Client = self.get_client()
        create_license(client, datetime(2023, 8, 28))
        with time_machine.travel(date(2023, 8, 14)):
            self.assertTrue(should_receive_notification(client))

    def test_with_license_expiring_within_a_month_and_is_tuesday(self):
        client:Client = self.get_client()
        create_license(client, datetime(2023, 8, 28))
        with time_machine.travel(date(2023, 8, 13)):
            self.assertFalse(should_receive_notification(client))
    
    def test_with_license_expiring_within_exactly_4_months(self):
        client:Client = self.get_client()
        create_license(client, datetime(2023, 12, 14))
        with time_machine.travel(date(2023, 8, 14)):
            self.assertTrue(should_receive_notification(client))

    def test_with_license_expiring_within_3_months(self):
        client:Client = self.get_client()
        create_license(client, datetime(2023, 11, 14))
        with time_machine.travel(date(2023, 8, 14)):
            self.assertFalse(should_receive_notification(client))

    def test_with_license_expiring_within_more_than_4_months(self):
        client:Client = self.get_client()
        create_license(client, datetime(2023, 12, 15))
        with time_machine.travel(date(2023, 8, 14)):
            self.assertFalse(should_receive_notification(client))

    def test_with_expired_license(self):
        client:Client = self.get_client()
        create_license(client, datetime(2023, 8, 13))
        with time_machine.travel(date(2023, 8, 14)):
            self.assertFalse(should_receive_notification(client))

    def test_with_license_expiring_today(self):
        client:Client = self.get_client()
        create_license(client, datetime(2023, 8, 14))
        with time_machine.travel(date(2023, 8, 14)):
            self.assertTrue(should_receive_notification(client))

    def test_with_many_licenses(self):
        client:Client = self.get_client()
        with time_machine.travel(date(2023, 8, 14)):
            create_license(client, datetime(2023, 12, 15))
            self.assertFalse(should_receive_notification(client))

            create_license(client, datetime(2023, 12, 13))
            create_license(client, datetime(2023, 11, 15))
            self.assertFalse(should_receive_notification(client))

            create_license(client, datetime(2023, 9, 15))
            self.assertFalse(should_receive_notification(client))

            create_license(client, datetime(2023, 7, 15))
            self.assertFalse(should_receive_notification(client))

            create_license(client, datetime(2023, 12, 14))
            self.assertTrue(should_receive_notification(client))
