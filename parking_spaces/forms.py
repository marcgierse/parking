import datetime

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.forms import ModelForm, ValidationError, EmailField, ModelChoiceField

from parking_spaces.models import ParkingSpace, RecurringFreeingEvents, ParkingSpaceRepresentative


class ParkingSpaceForm(ModelForm):
    class Meta:
        model = ParkingSpace
        fields = ['name', 'valid_from', 'valid_to']

    def clean(self):
        cleaned_data = super().clean()

        valid_from = cleaned_data.get("valid_from")
        valid_to = cleaned_data.get("valid_to")

        if valid_to is None or valid_from is None:
            raise ValidationError("Es müssen beide Datumsfelder in der Form TT.MM.JJJJ gefüllt sein!")

        if valid_from > valid_to:
            raise ValidationError("Das war Quatsch! Der Start des Mietvertrages muss vor dem Ende liegen!")

        if valid_to <= datetime.date.today():
            raise ValidationError("Ole Kamelle! Das Ende des Mietvertrages muss nach dem heutigen Tag liegen!")


class UserCreationFormWithMail(UserCreationForm):
    email = EmailField(required=True, help_text="Die Mailadresse wird nur zum Zusenden wichtiger Infos benötigt.")
    group = ModelChoiceField(required=True, queryset=Group.objects.all(), help_text="Zu welchem Parkplatzpool möchten Sie sich anmelden?", label="Parkplatzpool")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        user.groups.add(self.cleaned_data["group"])
        return user


class RecurringFreeingsForm(ModelForm):
    class Meta:
        model = RecurringFreeingEvents
        fields = ['mon', 'tue', 'wed', 'thu', 'fri']


class ParkingspaceRepresentativeForm(ModelForm):
    class Meta:
        model = ParkingSpaceRepresentative
        fields = ['user']


