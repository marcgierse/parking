from django.contrib import admin
from .models import ParkingSpace, ParkingSpaceEvent, RecurringFreeingEvents

# Register your models here.
admin.site.register(ParkingSpace)
admin.site.register(ParkingSpaceEvent)
admin.site.register(RecurringFreeingEvents)
