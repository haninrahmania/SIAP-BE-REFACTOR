from rest_framework import serializers
from .models import TrackerSurvei, JumlahResponden
from survei.serializers import SurveiGet

class TrackerSurveiSerializer(serializers.ModelSerializer):
    nama_survei = serializers.CharField(source='survei.nama_survei', read_only=True)
    nama_klien = serializers.CharField(source='survei.nama_klien', read_only=True)
    status = serializers.SerializerMethodField()
    latest_jumlah_responden = serializers.SerializerMethodField()
    cleaning_personil = serializers.CharField(read_only=True)
    updated_at = serializers.DateField(format="%Y-%m-%d")

    def get_latest_jumlah_responden(self, obj):
        last = obj.jumlah_responden.order_by('-updated_at').first()
        return last.jumlah if last else None
    
    class Meta:
        model = TrackerSurvei
        fields = ['id', 'nama_survei', 'nama_klien', 'status', 'last_status', 'latest_jumlah_responden', 'cleaning_personil', 'updated_at']
    
    def get_status(self, obj):
        status_fields = [
            # Administrasi Awal
            'buat_kontrak', 'buat_invoice_dp', 'pembayaran_dp', 'pembuatan_kwitansi_dp',
            # Logistik
            'terima_request_souvenir', 'ambil_souvenir',
            # Pengendali Mutu
            'pra_survei', 'turun_lapangan', 'pantau_responden', 'pantau_data_cleaning',
            # Administrasi Akhir
            'buat_invoice_final', 'pembuatan_laporan', 'pembayaran_lunas', 
            'pembuatan_kwitansi_final', 'penyerahan_laporan'
        ]
        return [{field: getattr(obj, field)} for field in status_fields]

class TrackerGet(serializers.ModelSerializer):
    survei = SurveiGet()
    status = serializers.SerializerMethodField()
    latest_jumlah_responden = serializers.SerializerMethodField()
    cleaning_personil = serializers.CharField(read_only=True)

    def get_latest_jumlah_responden(self, obj):
        last = obj.jumlahresponden_set.order_by('-updated_at').first()
        return last.jumlah if last else None

    
    class Meta:
        model = TrackerSurvei
        fields = ("id", "survei", "status", "last_status", "latest_jumlah_responden", "cleaning_personil")
    
    def get_status(self, obj):
        status_fields = [
            # Administrasi Awal
            'buat_kontrak', 'buat_invoice_dp', 'pembayaran_dp', 'pembuatan_kwitansi_dp',
            # Logistik
            'terima_request_souvenir', 'ambil_souvenir',
            # Pengendali Mutu
            'pra_survei', 'turun_lapangan', 'pantau_responden', 'pantau_data_cleaning',
            # Administrasi Akhir
            'buat_invoice_final', 'pembuatan_laporan', 'pembayaran_lunas', 
            'pembuatan_kwitansi_final', 'penyerahan_laporan'
        ]
        return [{field: getattr(obj, field)} for field in status_fields]
    
class JumlahRespondenSerializer(serializers.ModelSerializer):
    class Meta:
        model = JumlahResponden
        fields = ['id', 'jumlah', 'updated_at']
