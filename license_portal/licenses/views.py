
from licenses.utils import notify_license_expiration, licenses_that_needs_notification
from rest_framework.views import APIView
from rest_framework.response import Response


class NotifyLicenseExpiration(APIView):
    def post(self, request):
        clients_that_needs_notification = licenses_that_needs_notification().values_list(
            'client__id', flat=True
        ).distinct()

        for client_id in clients_that_needs_notification:
            notify_license_expiration(client_id)

        return Response(f"{clients_that_needs_notification.__len__()} client(s) notified.")
