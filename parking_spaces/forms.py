import datetime

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, ValidationError, EmailField

from parking_spaces.models import ParkingSpace


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

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user