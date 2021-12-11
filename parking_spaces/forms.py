import datetime

from django.forms import ModelForm, ValidationError

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