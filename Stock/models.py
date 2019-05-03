from django.db import models
from datetime import datetime
from django.utils import timezone
#Création des BDD

class Glace(models.Model):
    parfum_text = models.CharField(max_length=50)
    parfum_id = models.IntegerField(default=0)
    poids = models.FloatField(default=0)
    date_prod = models.DateField('date de production')
    date_dlc = models.DateField('date limite de consommation', default=timezone.now)
    no_lot = models.CharField(max_length=50)
    #Disponible ou Ordered ou Todo
    status = models.CharField(max_length = 20, default = "Disponible")
    #Labo, Nice, Cannes, Antibes
    franchise_name = models.CharField(max_length = 100, default = "None")
    commande_time = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.parfum_text
    def __str__(self):
        return self.status
    def __str__(self):
        return self.franchise_name


class Parfum(models.Model):
    parfum_text = models.CharField(max_length=50)
    sorbet = models.BooleanField(default=False)
    def __str__(self):
        return self.parfum_text

class Franchise(models.Model):
    franchise_name = models.CharField(max_length = 100)
    def __str__(self):
        return self.franchise_name
