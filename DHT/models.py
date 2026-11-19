from django.db import models
from django.utils import timezone

class Dht11(models.Model):
    temp = models.FloatField()
    hum = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.temp}°C - {self.hum}% ({self.date})"