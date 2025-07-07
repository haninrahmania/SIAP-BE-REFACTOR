from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from survei.models import Survei

class TrackerSurvei(models.Model):
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('FINISHED', 'Finished'),
        ('DELAYED', 'Delayed')
    ]

    survei = models.OneToOneField(
        Survei,
        on_delete=models.CASCADE,
        related_name='tracker'
    )

    # Administrasi Awal
    buat_kontrak = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    buat_invoice_dp = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    pembayaran_dp = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    pembuatan_kwitansi_dp = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')

    # Logistik
    terima_request_souvenir = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    ambil_souvenir = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')

    # Pengendali Mutu
    terima_info_survei = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    lakukan_survei = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    pantau_responden = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    pantau_data_cleaning = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')

    # Administrasi Akhir
    buat_invoice_final = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    pembuatan_laporan = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    pembayaran_lunas = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    pembuatan_kwitansi_final = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    penyerahan_laporan = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_status = models.CharField(max_length=100, null=True, blank=True)

    def update_last_status(self):
        # Check if penyerahan_laporan is finished first
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
                ('terima_info_survei', 'Terima Informasi Survei'),
                ('lakukan_survei', 'Lakukan Survei'),
                ('pantau_responden', 'Pantau Responden'),
                ('pantau_data_cleaning', 'Pantau Data Cleaning')
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

        # Iterate through all stages
        for stage in stages:
            for i, (field, description) in enumerate(stage):
                current_status = getattr(self, field)
                
                # If current field is not started and previous field is finished
                if current_status == 'NOT_STARTED':
                    if i == 0 or getattr(self, stage[i-1][0]) == 'FINISHED':
                        self.last_status = f"{description}: Not Started"
                        return
                
                # If current field is in progress
                elif current_status == 'IN_PROGRESS':
                    self.last_status = f"{description}: In Progress"
                    return
                
                # If current field is delayed
                elif current_status == 'DELAYED':
                    self.last_status = f"{description}: Delayed"
                    return
                
                # If current field is finished and it's the last field in the stage
                elif current_status == 'FINISHED' and i == len(stage) - 1:
                    continue

        # If no specific status is found, default to the first stage
        self.last_status = 'Buat Kontrak: Not Started'

    class Meta:
        db_table = 'tracker_survei'

    def is_administrasi_awal_finished(self):
        admin_awal_fields = [
            self.buat_kontrak,
            self.buat_invoice_dp,
            self.pembayaran_dp,
            self.pembuatan_kwitansi_dp
        ]
        return all(status == 'FINISHED' for status in admin_awal_fields)

    def is_logistik_finished(self):
        logistik_fields = [
            self.terima_request_souvenir,
            self.ambil_souvenir
        ]
        return all(status == 'FINISHED' for status in logistik_fields)

    def is_pengendali_mutu_finished(self):
        mutu_fields = [
            self.terima_info_survei,
            self.lakukan_survei,
            self.pantau_responden,
            self.pantau_data_cleaning
        ]
        return all(status == 'FINISHED' for status in mutu_fields)

    def is_administrasi_akhir_finished(self):
        admin_akhir_fields = [
            self.buat_invoice_final,
            self.pembuatan_laporan,
            self.pembayaran_lunas,
            self.pembuatan_kwitansi_final,
            self.penyerahan_laporan
        ]
        return all(status == 'FINISHED' for status in admin_akhir_fields)

    def clean(self):
        # Validate Administrasi Awal sequence
        if self.buat_invoice_dp != 'NOT_STARTED' and self.buat_kontrak != 'FINISHED':
            raise ValidationError('Buat Kontrak harus selesai sebelum Buat Invoice DP dapat dimulai')
        if self.pembayaran_dp != 'NOT_STARTED' and self.buat_invoice_dp != 'FINISHED':
            raise ValidationError('Buat Invoice DP harus selesai sebelum Pembayaran DP dapat dilakukan')
        if self.pembuatan_kwitansi_dp != 'NOT_STARTED' and self.pembayaran_dp != 'FINISHED':
            raise ValidationError('Pembayaran DP harus selesai sebelum Pembuatan Kwitansi DP dapat dibuat')

        # Validate Logistik sequence (after Administrasi Awal)
        logistik_fields = {'terima_request_souvenir', 'ambil_souvenir'}
        if any(getattr(self, field) != 'NOT_STARTED' for field in logistik_fields) and not self.is_administrasi_awal_finished():
            raise ValidationError('Semua tugas Administrasi Awal harus selesai sebelum memulai Logistik')

        # Validate Logistik internal sequence
        if self.ambil_souvenir != 'NOT_STARTED' and self.terima_request_souvenir != 'FINISHED':
            raise ValidationError('Menerima request souvenir harus selesai sebelum Mengambil souvenir dapat dimulai')

        # Validate Pengendali Mutu sequence (after Logistik)
        mutu_fields = {'terima_info_survei', 'lakukan_survei', 'pantau_responden', 'pantau_data_cleaning'}
        if any(getattr(self, field) != 'NOT_STARTED' for field in mutu_fields) and not self.is_logistik_finished():
            raise ValidationError('Semua tugas Logistik harus selesai sebelum memulai Pengendali Mutu')

        # Validate Pengendali Mutu internal sequence
        if self.lakukan_survei != 'NOT_STARTED' and self.terima_info_survei != 'FINISHED':
            raise ValidationError('Menerima informasi survei harus selesai sebelum Melakukan survei dapat dimulai')
        if self.pantau_responden != 'NOT_STARTED' and self.lakukan_survei != 'FINISHED':
            raise ValidationError('Melakukan survei harus selesai sebelum memantau responden yang sedang mengisi survei di lapangan')
        if self.pantau_data_cleaning != 'NOT_STARTED' and self.pantau_responden != 'FINISHED':
            raise ValidationError('Memantau responden harus selesai sebelum memantau data cleaning')

        # Validate Administrasi Akhir sequence (after Pengendali Mutu)
        admin_akhir_fields = {
            'pembuatan_laporan',
            'buat_invoice_final',
            'pembayaran_lunas',
            'pembuatan_kwitansi_final',
            'penyerahan_laporan'
        }
        if any(getattr(self, field) != 'NOT_STARTED' for field in admin_akhir_fields) and not self.is_pengendali_mutu_finished():
            raise ValidationError('Semua tugas Pengendali Mutu harus selesai sebelum memulai Administrasi Akhir')

        # Validate Administrasi Akhir internal sequence
        if self.buat_invoice_final != 'NOT_STARTED' and self.pembuatan_laporan != 'FINISHED':
            raise ValidationError('Pembuatan Laporan harus selesai sebelum Buat Invoice Final dapat dimulai')
            
        if self.pembayaran_lunas != 'NOT_STARTED' and self.buat_invoice_final != 'FINISHED':
            raise ValidationError('Buat Invoice Final harus selesai sebelum Pembayaran Lunas dapat dilakukan')
            
        if self.pembuatan_kwitansi_final != 'NOT_STARTED' and self.pembayaran_lunas != 'FINISHED':
            raise ValidationError('Pembayaran Lunas harus selesai sebelum Pembuatan Kwitansi Final dapat dibuat')
            
        if self.penyerahan_laporan != 'NOT_STARTED' and self.pembuatan_kwitansi_final != 'FINISHED':
            raise ValidationError('Pembuatan Kwitansi Final harus selesai sebelum Penyerahan Laporan dapat dilakukan')

    def save(self, *args, **kwargs):
        self.update_last_status()
        self.full_clean()
        super().save(*args, **kwargs)

    # @receiver(post_save, sender=Survei)
    # def create_tracker(sender, instance, created, **kwargs):
    #     if created:
    #         TrackerSurvei.objects.create(survei=instance)