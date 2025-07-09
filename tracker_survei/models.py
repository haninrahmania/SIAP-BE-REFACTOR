from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from survei.models import Survei

# Default shared statuses
STATUS_CHOICES_DEFAULT = [
    ('NOT_STARTED', 'Not Started'),
    ('IN_PROGRESS', 'In Progress'),
    ('FINISHED', 'Finished'),
    ('DELAYED', 'Delayed')
]

# Custom per-stage status choices
STATUS_CHOICES_PRA_SURVEI = STATUS_CHOICES_DEFAULT + [
    ('PRE_TEST', 'Pre-Test'),
    ('SKIP_PRE_TEST', 'Tidak Perlu Pre-Test')
]

STATUS_CHOICES_TURUN_LAPANGAN = STATUS_CHOICES_DEFAULT + [
    ('WORKSHOP', 'Workshop'),
    ('INPUT_DATA', 'Input Data'),
]

STATUS_CHOICES_PANTAU_CLEANING = STATUS_CHOICES_DEFAULT + [
    ('CLEANING', 'Cleaning in Progress'),
    ('CLEANED', 'Cleaned'),
]

class TrackerSurvei(models.Model):
    survei = models.OneToOneField(
        Survei,
        on_delete=models.CASCADE,
        related_name='tracker'
    )

    # Administrasi Awal
    buat_kontrak = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')
    buat_invoice_dp = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')
    pembayaran_dp = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')
    pembuatan_kwitansi_dp = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')

    # Logistik
    terima_request_souvenir = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')
    ambil_souvenir = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')

    # Pengendali Mutu
    pra_survei = models.CharField(max_length=30, choices=STATUS_CHOICES_PRA_SURVEI, default='NOT_STARTED')
    turun_lapangan = models.CharField(max_length=30, choices=STATUS_CHOICES_TURUN_LAPANGAN, default='NOT_STARTED')
    pantau_responden = models.BooleanField(default=False)
    pantau_data_cleaning = models.CharField(max_length=30, choices=STATUS_CHOICES_PANTAU_CLEANING, default='NOT_STARTED')
    cleaning_personil = models.CharField(max_length=255, null=True, blank=True)


    # Administrasi Akhir
    buat_invoice_final = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')
    pembuatan_laporan = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')
    pembayaran_lunas = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')
    pembuatan_kwitansi_final = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')
    penyerahan_laporan = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    last_status = models.CharField(max_length=100, null=True, blank=True)

    def update_last_status(self):
        # if self.penyerahan_laporan == 'FINISHED':
        #     self.last_status = 'Done'
        #     return

        # 1. Jika turun_lapangan selesai, tapi pantau_responden belum diisi
        if self.turun_lapangan in ['WORKSHOP', 'INPUT_DATA'] and not self.pantau_responden:
            self.last_status = "Memantau Responden: Not Started"
            return

        # 2. Jika pantau_responden sudah True, dan pantau_data_cleaning belum dimulai
        if self.pantau_responden and self.pantau_data_cleaning == 'NOT_STARTED':
            self.last_status = "Memantau Responden: In Progress"
            return

        # 3. Jika sedang cleaning
        if self.pantau_data_cleaning == 'CLEANING':
            self.last_status = "Memantau Data Cleaning: Cleaning in Progress"
            return

        # Mapping custom selesai
        custom_done_values = {
            'pra_survei': ['PRE_TEST', 'SKIP_PRE_TEST'],
            'turun_lapangan': ['WORKSHOP', 'INPUT_DATA'],
            'pantau_data_cleaning': ['CLEANED']
        }

        status_mapping = {
            'pra_survei': {
                'PRE_TEST': 'Pra-Survei: Pre-Test',
                'SKIP_PRE_TEST': 'Pra-Survei: Tidak Perlu Pre-Test'
            },
            'turun_lapangan': {
                'WORKSHOP': 'Turun Lapangan: Workshop',
                'INPUT_DATA': 'Turun Lapangan: Input Data'
            }
        }

        ordered_fields = [
            ('buat_kontrak', 'Buat Kontrak'),
            ('buat_invoice_dp', 'Buat Invoice DP'),
            ('pembayaran_dp', 'Pembayaran DP'),
            ('pembuatan_kwitansi_dp', 'Pembuatan Kwitansi DP'),
            ('terima_request_souvenir', 'Terima Request Souvenir'),
            ('ambil_souvenir', 'Ambil Souvenir'),
            ('pra_survei', 'Pra-Survei'),
            ('turun_lapangan', 'Turun Lapangan'),
            ('pantau_data_cleaning', 'Memantau Data Cleaning'),
            ('pembuatan_laporan', 'Pembuatan Laporan'),
            ('buat_invoice_final', 'Buat Invoice Final'),
            ('pembayaran_lunas', 'Pembayaran Lunas'),
            ('pembuatan_kwitansi_final', 'Pembuatan Kwitansi Final'),
            ('penyerahan_laporan', 'Penyerahan Laporan'),
        ]

        DONE_VALUES = {'FINISHED', 'PRE_TEST', 'SKIP_PRE_TEST', 'WORKSHOP', 'INPUT_DATA', 'CLEANED'}

        for i, (field, label) in enumerate(ordered_fields):
            value = getattr(self, field)

            # Tangani custom status selesai (tidak jadi last_status)
            if field in custom_done_values and value in custom_done_values[field]:
                continue

            if value == 'NOT_STARTED':
                if i == 0 or getattr(self, ordered_fields[i - 1][0]) in DONE_VALUES:
                    self.last_status = f"{label}: Not Started"
                    return
            elif value == 'IN_PROGRESS':
                self.last_status = f"{label}: In Progress"
                return
            elif value == 'DELAYED':
                self.last_status = f"{label}: Delayed"
                return

        # Jika semua status == NOT_STARTED dan pantau_responden False
        if all(
            getattr(self, field) == 'NOT_STARTED'
            for field, _ in ordered_fields
        ) and not self.pantau_responden:
            self.last_status = "Belum Dimulai"
            return

        # Jika semua selesai dan ada delay terhadap tanggal_selesai survei
        if all(
            getattr(self, field) in DONE_VALUES for field, _ in ordered_fields
        ) and self.pantau_responden:
            tanggal_selesai = self.survei.tanggal_selesai
            if tanggal_selesai and self.updated_at > tanggal_selesai:
                self.last_status = "Done with Delay"
            else:
                self.last_status = "Done"
            return

        self.last_status = "Buat Kontrak: Not Started"  # Fallback

    class Meta:
        db_table = 'tracker_survei'

    def is_administrasi_awal_finished(self):
        return all(getattr(self, field) == 'FINISHED' for field in [
            'buat_kontrak', 'buat_invoice_dp', 'pembayaran_dp', 'pembuatan_kwitansi_dp'
        ])

    def is_logistik_finished(self):
        return all(getattr(self, field) == 'FINISHED' for field in [
            'terima_request_souvenir', 'ambil_souvenir'
        ])

    def is_pengendali_mutu_finished(self):
        return (
            self.pra_survei in ['FINISHED', 'PRE_TEST', 'SKIP_PRE_TEST'] and
            self.turun_lapangan in ['WORKSHOP', 'INPUT_DATA'] and
            self.pantau_data_cleaning == 'CLEANED' and
            self.pantau_responden
        )

    def is_administrasi_akhir_finished(self):
        return all(getattr(self, field) == 'FINISHED' for field in [
            'buat_invoice_final', 'pembuatan_laporan', 'pembayaran_lunas', 'pembuatan_kwitansi_final', 'penyerahan_laporan'
        ])

    def clean(self):

        if self.buat_invoice_dp != 'NOT_STARTED' and self.buat_kontrak != 'FINISHED':
            raise ValidationError('Buat Kontrak harus selesai sebelum Buat Invoice DP dapat dimulai')
        if self.pembayaran_dp != 'NOT_STARTED' and self.buat_invoice_dp != 'FINISHED':
            raise ValidationError('Buat Invoice DP harus selesai sebelum Pembayaran DP dapat dilakukan')
        if self.pembuatan_kwitansi_dp != 'NOT_STARTED' and self.pembayaran_dp != 'FINISHED':
            raise ValidationError('Pembayaran DP harus selesai sebelum Pembuatan Kwitansi DP dapat dibuat')

        if any(getattr(self, field) != 'NOT_STARTED' for field in ['terima_request_souvenir', 'ambil_souvenir']) and not self.is_administrasi_awal_finished():
            raise ValidationError('Semua tugas Administrasi Awal harus selesai sebelum memulai Logistik')

        if self.ambil_souvenir != 'NOT_STARTED' and self.terima_request_souvenir != 'FINISHED':
            raise ValidationError('Menerima request souvenir harus selesai sebelum Mengambil souvenir dapat dimulai')

        if any(getattr(self, field) != 'NOT_STARTED' for field in ['pra_survei', 'turun_lapangan', 'pantau_data_cleaning']) and not self.is_logistik_finished():
            raise ValidationError('Semua tugas Logistik harus selesai sebelum memulai Pengendali Mutu')

        ALLOWED_PRA_SURVEI_DONE = ['FINISHED', 'PRE_TEST', 'SKIP_PRE_TEST']
        if self.turun_lapangan != 'NOT_STARTED' and self.pra_survei not in ALLOWED_PRA_SURVEI_DONE:
            raise ValidationError('Pra-Survei harus selesai sebelum Turun Lapangan')

        ALLOWED_TURUN_LAPANGAN = ['WORKSHOP', 'INPUT_DATA']
        if self.turun_lapangan!= 'NOT_STARTED' and self.turun_lapangan.strip() and self.turun_lapangan not in ALLOWED_TURUN_LAPANGAN:
            raise ValidationError('Turun Lapangan harus selesai sebelum Memantau responden dapat diisi')
            

        if self.pantau_data_cleaning != 'NOT_STARTED' and not self.pantau_responden:
            raise ValidationError('Memantau responden harus diisi sebelum bisa Memantau Data Cleaning')

        # if self.pantau_responden and self.pantau_responden.strip().lower() == 'n':
        if isinstance(self.pantau_responden, str) and self.pantau_responden.strip().lower() == 'n':
            raise ValidationError('Isian "pantau responden" tidak valid.')

        if any(getattr(self, field) != 'NOT_STARTED' for field in ['pembuatan_laporan', 'buat_invoice_final', 'pembayaran_lunas', 'pembuatan_kwitansi_final', 'penyerahan_laporan']) and not self.is_pengendali_mutu_finished():
            raise ValidationError('Semua tugas Pengendali Mutu harus selesai sebelum memulai Administrasi Akhir')

        if self.buat_invoice_final != 'NOT_STARTED' and self.pembuatan_laporan != 'FINISHED':
            raise ValidationError('Pembuatan Laporan harus selesai sebelum Buat Invoice Final dapat dimulai')
        if self.pembayaran_lunas != 'NOT_STARTED' and self.buat_invoice_final != 'FINISHED':
            raise ValidationError('Buat Invoice Final harus selesai sebelum Pembayaran Lunas dapat dilakukan')
        if self.pembuatan_kwitansi_final != 'NOT_STARTED' and self.pembayaran_lunas != 'FINISHED':
            raise ValidationError('Pembayaran Lunas harus selesai sebelum Pembuatan Kwitansi Final dapat dibuat')
        if self.penyerahan_laporan != 'NOT_STARTED' and self.pembuatan_kwitansi_final != 'FINISHED':
            raise ValidationError('Pembuatan Kwitansi Final harus selesai sebelum Penyerahan Laporan dapat dilakukan')

    def save(self, *args, **kwargs):
        self.full_clean()
        self.update_last_status()  # tambahkan ini agar last_status selalu update
        super().save(*args, **kwargs)

    @receiver(post_save, sender=Survei)
    def create_tracker(sender, instance, created, **kwargs):
        if created:
            TrackerSurvei.objects.create(survei=instance)

class JumlahResponden(models.Model):
    tracker = models.ForeignKey(
        TrackerSurvei,
        on_delete=models.CASCADE,
        related_name='jumlah_responden'  
    )
    jumlah = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jumlah_responden'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Responden: {self.jumlah} (Tracker ID {self.tracker_id})"
