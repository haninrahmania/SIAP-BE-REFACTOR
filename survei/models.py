from django.db import models
from django.utils import timezone
from klien.models import DataKlien

#test
class Survei(models.Model):
    SURVEI_CHOICE = {
        ("Paper-based", "Paper-based"),
        ("Digital", "Digital"),
        ("Lainnya", "Lainnya"),
    }
    RUANG_LINGKUP = {
        ("Nasional", "Nasional"),
        ("Provinsi", "Provinsi"),
        ("Kota", "Kota"),
    }

    nama_survei = models.CharField(
        default='',
        max_length=255,
        blank=False,
        null=False,
        unique=True
    )
    waktu_mulai_survei = models.DateTimeField(
        default=timezone.now,
        null=False,
        blank=False
    )

    waktu_berakhir_survei = models.DateTimeField(
        default=timezone.now,
        null=False,
        blank=False
    )
    klien = models.ForeignKey(
        DataKlien,
        on_delete=models.PROTECT,
        related_name='survei_set'
    )
    harga_survei = models.FloatField(default=0, null=False, blank=False)

    ruang_lingkup = models.CharField(
        max_length=255, choices=RUANG_LINGKUP, default='Nasional'
    )
    wilayah_survei = models.CharField(max_length=255, default="", null=False, blank=False)
    jumlah_responden = models.IntegerField(default=0, null=False, blank=False)
    tipe_survei = models.CharField(
        max_length=255,
        choices=SURVEI_CHOICE,
        default='Paper-based'
    )
    def __str__(self):
        return f"{self.nama_survei} - {self.klien.nama_perusahaan}"

    @property
    def nama_klien(self):
        """Maps to nama_perusahaan in DataKlien"""
        return self.klien.nama_perusahaan

    class Meta:
        db_table = 'survei'
    