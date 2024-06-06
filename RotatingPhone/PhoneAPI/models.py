from django.db import models

# Create your models here.
class Book(models.Model):
    id=models.IntegerField(primary_key=True)
    title=models.CharField(max_length=200)
    author=models.CharField(max_length=200)

class NMEA(models.Model):
    time = models.CharField(max_length = 200)
    PRN = models.CharField(max_length = 200)
    C_N0 = models.CharField(max_length = 200)
    ConstellationType = models.CharField(max_length = 200)
    SVID = models.CharField(max_length = 200)
    Azimuth = models.CharField(max_length = 200)
    Elevation = models.CharField(max_length = 200)
