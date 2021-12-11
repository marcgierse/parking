import json
import dataclasses

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from .models import ParkingSpace, ParkingSpaceEvent
from .forms import ParkingSpaceForm
import datetime

from .provider import ParkingSpaceStatusProvider, get_list_of_relevant_dates


@login_required()
def dashboard_view(request):
    data_provider = ParkingSpaceStatusProvider(current_user=request.user)
    result = data_provider.load_data()

    return render(request, "dashboard.html", context={"dates": get_list_of_relevant_dates(), "spaces": result,
                                                      "today": datetime.date.today()})


@login_required()
def freeing(request, parking_space, date):
    print(f"{parking_space=}")
    print(f"{date=}")

    already_exists = ParkingSpaceEvent.objects.filter(parking_space_id=parking_space, date=date,
                                                      status=ParkingSpaceEvent.FREE, deleted=False)
    if len(already_exists) != 0:
        print("freeing not possible")
        return redirect("dashboard")

    event = ParkingSpaceEvent.objects.create(status=ParkingSpaceEvent.FREE,
                                             parking_space_id=parking_space,
                                             date=date,
                                             user_id=request.user.id)

    event.save()
    return redirect("dashboard")


@login_required()
def reclaim(request, parking_space, date):
    print(f"{parking_space=}")
    print(f"{date=}")

    booked_by_user_event = ParkingSpaceEvent.objects.get(parking_space_id=parking_space, date=date, status=ParkingSpaceEvent.BOOKED_BY_USER, deleted=False)
    freed_by_owner = ParkingSpaceEvent.objects.get(parking_space_id=parking_space, date=date, status=ParkingSpaceEvent.FREE, deleted=False)

    booked_by_user_event.deleted = True
    freed_by_owner.deleted = True

    booked_by_user_event.save()
    freed_by_owner.save()

    return redirect("dashboard")


@login_required()
def booking(request, parking_space, date):
    print(f"{parking_space=}")
    print(f"{date=}")

    booking_possible = ParkingSpaceEvent.objects.filter(parking_space_id=parking_space, date=date,
                                                        status=ParkingSpaceEvent.FREE, deleted=False)
    if len(booking_possible) != 1:
        print("booking not possible (not free)")
        return redirect("dashboard")

    already_exists = ParkingSpaceEvent.objects.filter(parking_space_id=parking_space, date=date,
                                                      status=ParkingSpaceEvent.BOOKED_BY_USER,
                                                      deleted=False)
    if len(already_exists) != 0:
        print("booking not possible (already booked)")
        return redirect("dashboard")

    event = ParkingSpaceEvent.objects.create(status=ParkingSpaceEvent.BOOKED_BY_USER,
                                             parking_space_id=parking_space,
                                             date=date,
                                             user_id=request.user.id)

    event.save()
    return redirect("dashboard")


@login_required()
def delete_event(request, event_id):
    print(f"{event_id}=")

    event = ParkingSpaceEvent.objects.get(id=event_id)
    event.deleted = True
    event.save()

    return redirect("dashboard")


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def release_notes(request):
    return render(request, 'release_notes.html')


@login_required()
def parkingspaces(request):
    ps = ParkingSpace.objects.filter(owner=request.user, deleted=False)
    return render(request, "parking_spaces/parkingspaces.html", {"ps": ps})


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
def edit_parkingspace(request, parking_space):
    ps = ParkingSpace.objects.get(pk=parking_space)
    if request.method == 'POST':
        form = ParkingSpaceForm(request.POST, instance=ps)
        if form.is_valid():
            form.save()

            return redirect('parking_space')
    else:
        form = ParkingSpaceForm(instance=ps)
    return render(request, 'parking_spaces/parkingspace_form.html', {'form': form})


def delete_parkingspace(request, parking_space):
    ps = ParkingSpace.objects.get(pk=parking_space)
    ps.deleted = True
    ps.save()

    return redirect("parking_space")
