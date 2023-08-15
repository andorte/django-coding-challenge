
from licenses.utils import licenses_that_will_expire_soon, should_receive_notification, notify_license_expiration
from rest_framework.views import APIView
from rest_framework.response import Response


class NotifyLicenseExpiration(APIView):
    def post(self, request):
        clients_with_licenses_that_will_expire_soon = licenses_that_will_expire_soon().values_list(
            'client', flat=True
        ).distinct()

        notified_clients_qty:int = 0
        for client in clients_with_licenses_that_will_expire_soon:
            if should_receive_notification(client):
                notify_license_expiration(client)
                notified_clients_qty += 1

        return Response(f"{notified_clients_qty} client(s) notified.")
