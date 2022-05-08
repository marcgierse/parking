import logging.config
import time

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .models import ParkingSpace, ParkingSpaceEvent, RecurringFreeingEvents, ParkingSpaceRepresentative
from .forms import ParkingSpaceForm, UserCreationFormWithMail, RecurringFreeingsForm, ParkingspaceRepresentativeForm
import datetime

from .provider import ParkingSpaceStatusProvider, get_list_of_relevant_dates, find_users_of_same_group

logging.config.dictConfig(settings.LOGGING)
log = logging.getLogger('file')


@login_required()
def dashboard_view(request):
    log.info(f"Generiere Übersicht für User {request.user}")
    start = time.time()
    data_provider = ParkingSpaceStatusProvider(current_user=request.user)
    result = data_provider.load_data()
    log.debug(f"Suchdauer {time.time() - start}")
    return render(request, "dashboard.html", context={"dates": get_list_of_relevant_dates(), "spaces": result,
                                                      "today": datetime.date.today()})


@login_required()
def freeing(request, parking_space_id, date):
    log.info(f"starte 'Freigabe' von {parking_space_id=} am {date=} für User {request.user}")
    already_exists = ParkingSpaceEvent.objects.filter(parking_space_id=parking_space_id, date=date,
                                                      status=ParkingSpaceEvent.FREE, deleted=False)
    if already_exists.exists():
        log.warning(f"Freigabe nicht möglich! Es gibt bereits einen Datensatz, der den Parkplatz in dieser Situation freigibt.")
        for e in already_exists:
            log.warning(f"  {e}")
        return redirect("dashboard")

    event = ParkingSpaceEvent.objects.create(status=ParkingSpaceEvent.FREE,
                                             parking_space_id=parking_space_id,
                                             date=date,
                                             user_id=request.user.id)
    log.info("Freigabe erstellt -> wird nun abgespeichert")

    event.save()
    log.debug(f"Freigabe erfolgt unter {event.id=}")
    return redirect("dashboard")


@login_required()
def reclaim(request, parking_space_id, date):
    log.info(f"Starte 'reclaim' von {parking_space_id=} am {date=} durch User {request.user}")

    ps = ParkingSpace.objects.get(pk=parking_space_id)
    user_is_owner = ps.owner == request.user
    if user_is_owner:
        log.debug("ermittle 'Freigabe' und 'Buchung'-Events")
        booked_by_user_event = ParkingSpaceEvent.objects.get(parking_space_id=parking_space_id, date=date, status=ParkingSpaceEvent.BOOKED_BY_USER, deleted=False)
        freed_by_owner = ParkingSpaceEvent.objects.get(parking_space_id=parking_space_id, date=date, status=ParkingSpaceEvent.FREE, deleted=False)
        log.info(f"Setze das Löschflag bei {booked_by_user_event.id=} und {freed_by_owner.id=}")
        booked_by_user_event.deleted = True
        freed_by_owner.deleted = True

        booked_by_user_event.save()
        freed_by_owner.save()
        log.debug("speichere beide Events mit Löschflag ab.")
    else:
        # Wir sind im Fall, dass ein Vertreter den Reclaim angefragt hat. In diesem Fall, löschen wir die
        # 'booked'-Buchung und fügen eine neue vom anfordernen User hinzu.
        try:
            rep = ParkingSpaceRepresentative.objects.get(parking_space_id=parking_space_id, user_id=request.user.id, deleted=False)
        except ParkingSpaceRepresentative.DoesNotExist:
            log.error("reclaim wurde angefragt, von User, der kein Vertreter ist.")

        booked_by_user_event = ParkingSpaceEvent.objects.get(parking_space_id=parking_space_id, date=date,
                                                             status=ParkingSpaceEvent.BOOKED_BY_USER, deleted=False)
        booked_by_user_event.deleted = True
        booked_by_user_event.save()
        event = ParkingSpaceEvent.objects.create(status=ParkingSpaceEvent.BOOKED_BY_USER,
                                                 parking_space_id=parking_space_id,
                                                 date=date,
                                                 user_id=request.user.id)
        event.save()

    return redirect("dashboard")


@login_required()
def booking(request, parking_space_id, date):
    log.info(f"Starte 'Buchung' von {parking_space_id=} am {date=} durch User {request.user}")

    booking_possible = ParkingSpaceEvent.objects.filter(parking_space_id=parking_space_id, date=date,
                                                        status=ParkingSpaceEvent.FREE, deleted=False)
    if not booking_possible.exists():
        log.warning("Es wurde keine Freigabebuchung gefunden. -> Keine Buchung möglich")
        return redirect("dashboard")

    already_booked = ParkingSpaceEvent.objects.filter(parking_space_id=parking_space_id, date=date,
                                                      status=ParkingSpaceEvent.BOOKED_BY_USER,
                                                      deleted=False)
    if already_booked.exists():
        log.warning("Buchung nicht möglich, da der Parkplatz bereits gebucht wurde:")
        return redirect("dashboard")

    event = ParkingSpaceEvent.objects.create(status=ParkingSpaceEvent.BOOKED_BY_USER,
                                             parking_space_id=parking_space_id,
                                             date=date,
                                             user_id=request.user.id)

    event.save()
    return redirect("dashboard")


@login_required()
def delete_event(request, event_id):
    log.info(f"Event mit {event_id=} mit Löschflag versehen durch User {request.user}")

    event = ParkingSpaceEvent.objects.get(id=event_id)
    event.deleted = True
    event.save()

    return redirect("dashboard")


def signup(request):
    if request.method == 'POST':
        form = UserCreationFormWithMail(request.POST)
        if form.is_valid():
            user = form.save()
            # username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user.set_password(raw_password)
            user.save()
            # user = authenticate(username=username, password=raw_password)
            login(request, user)

            return redirect('dashboard')
    else:
        form = UserCreationFormWithMail()
    return render(request, 'registration/signup.html', {'form': form})


def release_notes(request):
    return render(request, 'release_notes.html')


@login_required()
def parkingspaces(request):
    today = datetime.date.today()
    ps = ParkingSpace.objects.filter(owner=request.user, deleted=False)
    return render(request, "parking_spaces/parkingspaces.html", {"ps": ps, "today": today})


@login_required()
def add_parkingspace(request):
    if request.method == 'POST':
        form = ParkingSpaceForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.owner = request.user
            form.save()

            return redirect('parking_space')
    else:
        form = ParkingSpaceForm()
    return render(request, 'parking_spaces/parkingspace_form.html', {'form': form})


@login_required()
def edit_parkingspace(request, parking_space_id):
    ps = ParkingSpace.objects.get(pk=parking_space_id)
    if request.method == 'POST':
        form = ParkingSpaceForm(request.POST, instance=ps)
        if form.is_valid():
            form.save()

            return redirect('parking_space')
    else:
        form = ParkingSpaceForm(instance=ps)
    return render(request, 'parking_spaces/parkingspace_form.html', {'form': form})


@login_required()
def delete_parkingspace(request, parking_space_id):
    log.info(f"setze Löschflag für {parking_space_id=}")
    ps = ParkingSpace.objects.get(pk=parking_space_id)
    ps.deleted = True
    ps.save()

    return redirect("parking_space")


@login_required()
def manage_recurring_freeings(request, parking_space_id):
    try:
        rf = RecurringFreeingEvents.objects.get(parking_space_id=parking_space_id)
    except RecurringFreeingEvents.DoesNotExist:
        rf = RecurringFreeingEvents()
        rf.parking_space_id = parking_space_id
    if request.method == 'POST':
        form = RecurringFreeingsForm(request.POST, instance=rf)
        if form.is_valid():
            form.save()
        return redirect('parking_space')
    else:
        form = RecurringFreeingsForm(instance=rf)
    return render(request, 'parking_spaces/recurring_freeing.html', {'form': form})


@login_required()
def manage_representatives(request, parking_space_id):
    reps = ParkingSpaceRepresentative.objects.filter(parking_space_id=parking_space_id, deleted=False)
    if request.method == 'POST':
        rep = ParkingSpaceRepresentative()
        rep.parking_space_id = parking_space_id
        form = ParkingspaceRepresentativeForm(request.POST, instance=rep)

        if form.is_valid():
            form.save()
        return redirect('manage_representatives', parking_space_id)
    else:
        rep = ParkingSpaceRepresentative()
        rep.parking_space_id = parking_space_id
        form = ParkingspaceRepresentativeForm(instance=rep)

        form.fields["user"].queryset = find_users_of_same_group(request.user).exclude(
            username__in=[str(r.user) for r in reps]).exclude(username__in=[str(request.user)])
    return render(request, 'parking_spaces/parkingspace_representative.html', {'form': form, 'reps': reps})


@login_required()
def delete_parkingspace_representative(request, rep_id):
    log.info(f"setze Löschflag für Vertretung {rep_id=}")
    try:
        rep = ParkingSpaceRepresentative.objects.get(pk=rep_id)
    except ParkingSpaceRepresentative.DoesNotExist:
        log.warning(f"Kein Datensatz mit {rep_id=} gefunden.")
        return redirect('parking_space')

    rep.deleted = True
    rep.save()

    return redirect("manage_representatives", rep.parking_space_id)


def help_page(request):
    return render(request, 'help.html')
