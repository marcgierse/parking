import dataclasses
import datetime
from typing import Optional, List

from django.contrib.auth.models import User

from parking_spaces.models import ParkingSpace, ParkingSpaceEvent


def get_list_of_relevant_dates(number_of_weeks=2):
    today = datetime.date.today()
    weekday = today.isoweekday()
    # The start of the week
    start = today - datetime.timedelta(days=weekday - 1)
    # build a simple range
    dates = [start + datetime.timedelta(days=d + (7 * w)) for w in range(number_of_weeks) for d in range(5)]
    return dates


@dataclasses.dataclass
class ParkingSpaceStatus:
    date: datetime.date
    latest_event: Optional[ParkingSpaceEvent]
    action: str
    status: str


@dataclasses.dataclass
class ParkingSpaceStatusList:
    parking_space_info: ParkingSpace
    status: List[ParkingSpaceStatus]


class ParkingSpaceStatusProvider:
    def __init__(self, current_user: User, date: Optional[datetime.date] = None):
        self.current_user = current_user
        if date is None:
            date = datetime.date.today()
        self.today: datetime.date = date
        self.active_parking_spaces: List[ParkingSpace] = ParkingSpace.objects.filter(valid_to__gt=self.today,
                                                                                     valid_from__lte=self.today,
                                                                                     deleted=False)
        self.relevant_dates: List[datetime.date] = get_list_of_relevant_dates()
        self.relevant_events: List[ParkingSpaceEvent] = ParkingSpaceEvent.objects.filter(date__in=self.relevant_dates,
                                                                                         deleted=False)
        self.result_struct: List[ParkingSpaceStatusList] = []

    def _user_already_has_a_parking_space_booked(self, date: datetime.date) -> bool:
        for ps in self.active_parking_spaces:
            if ps.owner_id == self.current_user.id:
                return True

        query = ParkingSpaceEvent.objects.filter(user_id=self.current_user.id, deleted=False, date=date,
                                                 status=ParkingSpaceEvent.BOOKED_BY_USER)
        if len(query) > 0:
            return True

        return False

    def _init_result_struct(self):
        for ps in self.active_parking_spaces:
            ps_status_list: ParkingSpaceStatusList = ParkingSpaceStatusList(parking_space_info=ps, status=[])
            for d in self.relevant_dates:
                status = ParkingSpaceStatus(latest_event=self._find_latest_event(ps, d), action="", status="", date=d)
                status.action = self._determine_possible_action(parking_space=ps, current_status=status.latest_event,
                                                                date=d)
                status.status = status.latest_event.status if status.latest_event is not None else ParkingSpaceEvent.USED_BY_OWNER
                ps_status_list.status.append(status)

            self.result_struct.append(ps_status_list)

    def _find_latest_event(self, parking_space: ParkingSpace, date: datetime.date) -> Optional[ParkingSpaceEvent]:
        # sollte nicht vorkommen können
        if date not in self.relevant_dates:
            return None

        # sollte auch eigentlich nicht vorkommen können.
        if parking_space not in self.active_parking_spaces:
            return None

        if (parking_space.valid_to < date) or (parking_space.valid_from > date):
            return ParkingSpaceEvent(status=ParkingSpaceEvent.INACTIVE, date=date, parking_space=parking_space)

        event_query = [e for e in self.relevant_events if parking_space.id == e.parking_space.id and
                       date == e.date]

        # kein Event gefunden -> es wurde bislang nichts gebucht.
        if len(event_query) == 0:
            return None

        event_query.sort(key=lambda x: x.modified)
        if len(event_query) > 1:
            print(event_query)
        latest_event = event_query[-1]

        return latest_event

    def _determine_possible_action(self, parking_space: ParkingSpace,
                                   current_status: Optional[ParkingSpaceEvent],
                                   date: datetime.date) -> str:
        # wenn der Tag vor heute liegt, gibt es gar keine mögliche Aktionen
        if date < self.today:
            return ""

        current_user_is_owner = parking_space.owner_id == self.current_user.id
        # None heißt keine Buchung -> Nur der Besitzer kann freigeben
        if current_status is None:
            if current_user_is_owner:
                return "FREE"
            else:
                return ""

        if current_status == ParkingSpaceEvent.INACTIVE:
            return ""

        # falls die Freigabe erteilt wurde, kann jeder buchen, außer der Besitzer -> dieser kann die Freigabe löschen
        if current_status.status == ParkingSpaceEvent.FREE:
            if current_user_is_owner:
                return "DELETE"
            else:
                if self._user_already_has_a_parking_space_booked(date):
                    return ""
                else:
                    return "BOOK"

        # falls ein User gebucht hat, kann der Besitzer den Platz zurückfordern, der buchende User kann den Platz wieder
        # freigaben - alle anderen können nichts tun.
        if current_status.status == ParkingSpaceEvent.BOOKED_BY_USER:
            if current_user_is_owner:
                return "RECLAIM"
            elif self.current_user.id == current_status.user_id:
                return "DELETE"
            else:
                return ""

    def load_data(self):
        self._init_result_struct()
        return self.result_struct
