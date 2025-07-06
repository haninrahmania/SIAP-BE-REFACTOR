from django.db import models

# Create your models here.
class Souvenir(models.Model):
    KATEGORI_CHOICES = [
        ('fisik', 'Fisik'),
        ('non-fisik', 'Non-Fisik'),
    ]

    nama_souvenir = models.CharField(default='', max_length=255, blank=False, null=False, unique=True)
    jumlah_stok = models.IntegerField(default=0, null=False, blank=False)
    jumlah_minimum = models.IntegerField(default=0, null=False, blank=False)
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='fisik')
    harga_per_pcs = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    nama_vendor = models.CharField(max_length=255, blank=True, null=True)
    kontak_vendor = models.CharField(max_length=100, blank=True, null=True)
    tanggal_order = models.DateField(blank=True, null=True)
    tanggal_diterima = models.DateField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.nama_souvenir
