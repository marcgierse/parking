#!/home/pypark/venv/bin/python
import os
import datetime

import django

#  you have to set the correct path to you settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parking.settings")
django.setup()
from parking_spaces.models import RecurringFreeingEvents, ParkingSpaceEvent, ParkingSpace


def check_if_parking_space_is_active(parking_space: ParkingSpace, date: datetime.date) -> bool:
    if parking_space.deleted:
        return False

    if parking_space.valid_from > date:
        return False

    if parking_space.valid_to < date:
        return False

    return True


if __name__ == "__main__":
    today = datetime.date.today()
    # find monday of week after next
    monday_of_week_after_next = today + datetime.timedelta(days=14) - datetime.timedelta(days=today.weekday())
    print(monday_of_week_after_next)

    recurring_frees = RecurringFreeingEvents.objects.all()
    for r in recurring_frees:
        for d in r.find_dates_to_free(monday_of_week_after_next):
            if not check_if_parking_space_is_active(r.parking_space, d):
                continue
            if ParkingSpaceEvent.objects.filter(status=ParkingSpaceEvent.FREE, date=d, deleted=False,
                                                parking_space_id=r.parking_space_id).exists():
                continue
            ParkingSpaceEvent(user_id=r.parking_space.owner_id,
                              parking_space_id=r.parking_space_id,
                              date=d,
                              status=ParkingSpaceEvent.FREE).save()

