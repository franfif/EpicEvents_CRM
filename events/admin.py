from django.contrib import admin
from events.models import Event, EventStatus

admin.site.register(Event)
admin.site.register(EventStatus)
