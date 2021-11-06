from django.contrib import admin
from .models import ParkingSpace, ParkingSpaceEvent

# Register your models here.
admin.site.register(ParkingSpace)
admin.site.register(ParkingSpaceEvent)
