from django.db import models

# Create your models here.
class Souvenir(models.Model):
    nama_souvenir = models.CharField(default='', max_length=255, blank=False, null=False, unique=True)
    jumlah_stok = models.IntegerField(default=0, null=False, blank=False)
    jumlah_minimum = models.IntegerField(default=0, null=False, blank=False)
    is_deleted = models.BooleanField(default=False) 