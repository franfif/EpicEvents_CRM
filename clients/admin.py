from django.contrib import admin
from clients.models import Client, ClientStatus


admin.site.register(Client)
admin.site.register(ClientStatus)
