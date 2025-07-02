from django.db import models
from django.db.models import JSONField
from klien.models import DataKlien
from souvenir.models import Souvenir

class Survei(models.Model):
    JENIS_SURVEI = [
        ("Elektoral", "Elektoral"),
        ("Tematik", "Tematik"),
    ]
    RUANG_LINGKUP = {
        ("Nasional", "Nasional"),
        ("Provinsi", "Provinsi"),
        ("Kota", "Kota"),
        ("Dapil", "Dapil"),
    }
    SURVEI_CHOICE = {
        ("Telepon", "Telepon"),
        ("Tatap muka", "Tatap muka"),
        ("Online", "Online"),
    }

    # Section 1: Basic Info
    judul_survei = models.CharField(max_length=255, unique=True, default="")
    klien = models.ForeignKey(
        DataKlien,
        on_delete=models.PROTECT,
        related_name='survei_set'
    )
    jenis_survei = models.CharField(max_length=50, choices=JENIS_SURVEI, default="Elektoral")
    ruang_lingkup = models.CharField(max_length=50, choices=RUANG_LINGKUP, default="Nasional")

    # Section 2: Wilayah Survei
    wilayah_survei = JSONField(default=list, blank=True)

    # Section 3: Detail Survei
    tipe_survei = models.CharField(max_length=50, choices=SURVEI_CHOICE, default="Paper-based")
    jumlah_responden = models.IntegerField(default=0)
    harga_survei = models.FloatField(default=0)
    tanggal_spk = models.DateField(null=True, blank=True)
    tanggal_ws = models.DateField(null=True, blank=True)
    tanggal_selesai = models.DateField(null=True, blank=True)
    milestone_1 = models.DateField(null=True, blank=True)
    milestone_2 = models.DateField(null=True, blank=True)
    milestone_3 = models.DateField(null=True, blank=True)
    ppk = JSONField(default=list, blank=True)
    peneliti = JSONField(default=list, blank=True)
    jumlah_souvenir = models.IntegerField(default=0, null=True, blank=True)

    # Section 4: Souvenir
    souvenir = models.ForeignKey(
        Souvenir,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='survei_dengan_souvenir'
    )

    def __str__(self):
        return f"{self.judul_survei} - {self.klien}"

    @property
    def nama_klien(self):
        return str(self.klien)

    class Meta:
        db_table = 'survei'