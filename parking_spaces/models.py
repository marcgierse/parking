from django.db import models


# Create your models here.
class ParkingSpace(models.Model):
    owner = models.CharField(max_length=20)
    name = models.CharField(max_length=40)
    valid_from = models.DateField()
    valid_to = models.DateField()

    def __str__(self):
        return self.name


class ParkingSpaceEvent(models.Model):
    status = models.CharField(max_length=10)
    parking_space = models.ForeignKey(to='ParkingSpace', on_delete=models.CASCADE)
    date = models.DateField()
    user = models.CharField(blank=True, max_length=20, )

    def __str__(self):
        return f"{self.parking_space.name} - {self.date} - {self.status}"

