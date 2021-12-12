from django.conf import settings
from django.db import models


# Create your models here.
class ParkingSpace(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Besitzer")
    name = models.CharField(max_length=40, verbose_name="Parkplatzname")
    valid_from = models.DateField(verbose_name="Start Mietvertrag", help_text="Ab wann steht der Mietvertrag "
                                                                              "grundsätzlich zur Verfügung? (TT.MM.JJJJ)")
    valid_to = models.DateField(verbose_name="Ende Mietvertrag", help_text="Bis wann steht der Parkplatz "
                                                                           "grundsätzlich zur Verfügung? (TT.MM.JJJJ)")
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.owner})"


class ParkingSpaceEvent(models.Model):
    UNKNOWN = "UNKNOWN"
    INACTIVE = "INACTIVE"
    USED_BY_OWNER = "USED_OWNER"
    FREE = "FREE"
    BOOKED_BY_USER = "USED_USER"
    STATUS_CHOICES = [
        (USED_BY_OWNER, "USED_BY_OWNER"),
        (FREE, "FREE"),
        (BOOKED_BY_USER, "BOOKED_BY_USER"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    parking_space = models.ForeignKey(to='ParkingSpace', on_delete=models.CASCADE)
    date = models.DateField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.deleted:
            return " - ".join(["deleted", self.parking_space.name, str(self.date), self.status, str(self.user)])
        return " - ".join([self.parking_space.name, str(self.date), self.status, str(self.user)])


