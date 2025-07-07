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
    pantau_responden = models.IntegerField(max_length=10000, blank=True, null=True)  
    pantau_data_cleaning = models.CharField(max_length=30, choices=STATUS_CHOICES_PANTAU_CLEANING, default='NOT_STARTED')

    # Administrasi Akhir
    buat_invoice_final = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')
    pembuatan_laporan = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')
    pembayaran_lunas = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')
    pembuatan_kwitansi_final = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')
    penyerahan_laporan = models.CharField(max_length=20, choices=STATUS_CHOICES_DEFAULT, default='NOT_STARTED')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_status = models.CharField(max_length=100, null=True, blank=True)

    def update_last_status(self):
        if self.penyerahan_laporan == 'FINISHED':
            self.last_status = 'Done'
            return

        stages = [
            # Administrasi Awal
            [
                ('buat_kontrak', 'Buat Kontrak'),
                ('buat_invoice_dp', 'Buat Invoice DP'),
                ('pembayaran_dp', 'Pembayaran DP'),
                ('pembuatan_kwitansi_dp', 'Pembuatan Kwitansi DP')
            ],
            # Logistik
            [
                ('terima_request_souvenir', 'Terima Request Souvenir'),
                ('ambil_souvenir', 'Ambil Souvenir')
            ],
            # Pengendali Mutu
            [
                ('pra_survei', 'Pra-Survei'),
                ('turun_lapangan', 'Turun Lapangan'),
                ('pantau_data_cleaning', 'Memantau Data Cleaning')
            ],
            # Administrasi Akhir
            [
                ('pembuatan_laporan', 'Pembuatan Laporan'),
                ('buat_invoice_final', 'Buat Invoice Final'),
                ('pembayaran_lunas', 'Pembayaran Lunas'),
                ('pembuatan_kwitansi_final', 'Pembuatan Kwitansi Final'),
                ('penyerahan_laporan', 'Penyerahan Laporan')
            ]
        ]

        for stage in stages:
            for i, (field, description) in enumerate(stage):
                current_status = getattr(self, field)

                if field == 'pantau_responden':
                    if self.pantau_responden:
                         self.last_status = "Memantau Responden: In Progress"
                         # This is not a blocking step, so we don't return
                    continue

                if current_status == 'NOT_STARTED':
                    if i == 0 or getattr(self, stage[i-1][0]) == 'FINISHED':
                        self.last_status = f"{description}: Not Started"
                        return
                elif current_status == 'IN_PROGRESS':
                    self.last_status = f"{description}: In Progress"
                    return
                elif current_status == 'DELAYED':
                    self.last_status = f"{description}: Delayed"
                    return

        self.last_status = 'Buat Kontrak: Not Started'

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
        return all(getattr(self, field) == 'FINISHED' for field in [
            'pra_survei', 'turun_lapangan', 'pantau_data_cleaning'
        ])

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
            

        if self.pantau_data_cleaning != 'NOT_STARTED' and self.turun_lapangan != 'FINISHED':
            raise ValidationError('Memantau responden harus diisi sebelum bisa Memantau Data Cleaning')

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
        # self.update_last_status()
        super().save(*args, **kwargs)

    @receiver(post_save, sender=Survei)
    def create_tracker(sender, instance, created, **kwargs):
        if created:
            TrackerSurvei.objects.create(survei=instance)
