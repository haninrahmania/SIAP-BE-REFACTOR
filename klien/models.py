# from django.db import models

# class DataKlien(models.Model):
#     nama_klien = models.CharField(max_length=50)
#     nama_perusahaan = models.CharField(max_length=100)
#     daerah = models.TextField()
#     is_deleted = models.BooleanField(default=False)

from django.db import models

class DataKlien(models.Model):
    KATEGORI_KLIEN_CHOICES = [
        ('individu', 'Individu'),
        ('partai', 'Partai'),
        ('perusahaan', 'Perusahaan'),
        ('lainnya', 'Lainnya'),
    ]

    nama_klien = models.CharField(max_length=50)
    nama_perusahaan = models.CharField(max_length=100)
    jabatan = models.TextField()
    daerah = models.TextField()
    kategori_klien = models.CharField(
        max_length=20,
        choices=KATEGORI_KLIEN_CHOICES,
        default='lainnya'
    )
    no_telp = models.CharField(max_length=12, blank=False)
    dokumen_pendukung = models.FileField(upload_to='dokumen_klien/', blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.nama_klien