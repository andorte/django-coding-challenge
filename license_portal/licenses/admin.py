from django.contrib import admin
from licenses.models import Client, License

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    pass
