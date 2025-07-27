import datetime
from rest_framework import serializers
from .models import Survei
from souvenir.models import Souvenir
from tracker_survei.models import JumlahResponden
from klien.models import DataKlien
from django.utils import timezone
from num2words import num2words

class DataKlienSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = DataKlien
        fields = ['id', 'nama_perusahaan', 'nama_klien', 'display_name']

    def get_display_name(self, obj):
        return f"{obj.nama_perusahaan} - {obj.nama_klien}"


class SurveiGet(serializers.ModelSerializer):
    nama_klien = serializers.SerializerMethodField()
    wilayah_survei_names = serializers.SerializerMethodField()
    ppk = serializers.SerializerMethodField()
    peneliti = serializers.SerializerMethodField()
    souvenir = serializers.SerializerMethodField()
    jumlah_responden_harian = serializers.SerializerMethodField()

    class Meta:
        model = Survei
        fields = (
            'id', 'judul_survei', 'nama_klien', 'jenis_survei',
            'ruang_lingkup', 'wilayah_survei', 'wilayah_survei_names',
            'tipe_survei', 'jumlah_responden', 'harga_survei',
            'tanggal_spk', 'tanggal_ws', 'tanggal_selesai',
            'milestone_1', 'milestone_2', 'milestone_3',
            'souvenir', 'ppk', 'peneliti', 'jumlah_souvenir', 'jumlah_responden_harian', 'klien_id', 'nomor_spk', 'harga_survei_terbilang'
        )

    def get_nama_klien(self, obj):
        if obj.klien:
            return f"{obj.klien.nama_perusahaan} - {obj.klien.nama_klien}"
        return "-"

    def get_wilayah_survei_names(self, obj):
        if isinstance(obj.wilayah_survei, list):
            return [w.get("name", "") for w in obj.wilayah_survei if isinstance(w, dict)]
        elif isinstance(obj.wilayah_survei, str):
            return [item.strip() for item in obj.wilayah_survei.split(",")]
        return []

    def get_ppk(self, obj):
        return obj.ppk or []

    def get_peneliti(self, obj):
        return obj.peneliti or []

    def get_souvenir(self, obj):
        if obj.souvenir:
            return {
                "id": obj.souvenir.id,
                "nama_souvenir": obj.souvenir.nama_souvenir,
                "jumlah_stok": obj.souvenir.jumlah_stok,
                "jumlah_minimum": obj.souvenir.jumlah_minimum,
            }
        return None

    def get_jumlah_responden_harian(self, obj):
        tracker = getattr(obj, "tracker", None)
        if not tracker:
            return []

        return JumlahRespondenSerializer(tracker.jumlah_responden.all(), many=True).data

class SurveiPost(serializers.ModelSerializer):
    klien_id = serializers.PrimaryKeyRelatedField(
        queryset=DataKlien.objects.all(),
        source='klien',
        write_only=True
    )
    nama_klien = serializers.SerializerMethodField(read_only=True)
    wilayah_survei = serializers.ListField(child=serializers.DictField(), write_only=True)
    wilayah_survei_names = serializers.SerializerMethodField(read_only=True)
    souvenir = serializers.PrimaryKeyRelatedField(queryset=Souvenir.objects.all(), allow_null=True, required=False)
    ppk = serializers.ListField(child=serializers.DictField(), required=False)
    peneliti = serializers.ListField(child=serializers.DictField(), required=False)

    class Meta:
        model = Survei
        fields = (
            'id', 'judul_survei', 'klien_id', 'nama_klien', 'jenis_survei',
            'ruang_lingkup', 'wilayah_survei', 'wilayah_survei_names',
            'tipe_survei', 'jumlah_responden', 'harga_survei',
            'tanggal_spk', 'tanggal_ws', 'tanggal_selesai',
            'milestone_1', 'milestone_2', 'milestone_3',
            'souvenir', 'ppk', 'peneliti', 'jumlah_souvenir', 'nomor_spk', 'harga_survei_terbilang'
        )

    def get_nama_klien(self, obj):
        if obj.klien:
            return DataKlienSerializer(obj.klien).data.get("display_name")
        return None

    def get_wilayah_survei_names(self, obj):
        if isinstance(obj.wilayah_survei, list):
            return [w.get("name", "") for w in obj.wilayah_survei if isinstance(w, dict)]
        elif isinstance(obj.wilayah_survei, str):
            return [item.strip() for item in obj.wilayah_survei.split(",")]
        return []

    def validate_wilayah_survei(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("wilayah_survei must be a list.")
        for item in value:
            if 'name' not in item:
                raise serializers.ValidationError("Each item must have a 'name' field.")
        return value

    def validate(self, attrs):
        jenis = attrs.get("jenis_survei")

        if jenis == "Elektoral":
            # Kosongkan milestone
            attrs["milestone_1"] = None
            attrs["milestone_2"] = None
            attrs["milestone_3"] = None

        else:
            # Pastikan milestone dalam format tanggal yang valid
            for field in ['milestone_1', 'milestone_2', 'milestone_3']:
                value = attrs.get(field)
                if value:
                    if isinstance(value, str):
                        try:
                            attrs[field] = datetime.strptime(value, "%Y-%m-%d").date()
                        except ValueError:
                            raise serializers.ValidationError({
                                field: "Format tanggal salah. Gunakan format YYYY-MM-DD."
                            })

        return attrs

    def update(self, instance, validated_data):
        # Handle harga_survei_terbilang
        if 'harga_survei' in validated_data:
            harga = validated_data['harga_survei']
            if harga is not None:
                validated_data['harga_survei_terbilang'] = num2words(int(harga), lang='id').title() + " Rupiah"

        # Handle stok souvenir
        old_souvenir = instance.souvenir
        old_jumlah = instance.jumlah_souvenir or 0

        new_souvenir = validated_data.get('souvenir', old_souvenir)
        new_jumlah = validated_data.get('jumlah_souvenir', old_jumlah)

        # Validasi stok (optional, tapi best practice)
        if new_souvenir == old_souvenir and new_souvenir:
            diff = new_jumlah - old_jumlah
            if diff > 0 and new_souvenir.jumlah_stok < diff:
                raise serializers.ValidationError("Stok souvenir tidak mencukupi.")
        elif new_souvenir != old_souvenir and new_souvenir:
            if new_souvenir.jumlah_stok < new_jumlah:
                raise serializers.ValidationError("Stok souvenir tidak mencukupi.")

        # Simpan perubahan instance
        instance = super().update(instance, validated_data)

        # Update stok
        if old_souvenir == new_souvenir:
            diff = new_jumlah - old_jumlah
            if diff != 0 and new_souvenir:
                new_souvenir.jumlah_stok -= diff
                new_souvenir.save()
        else:
            if old_souvenir:
                old_souvenir.jumlah_stok += old_jumlah
                old_souvenir.save()
            if new_souvenir and new_jumlah:
                new_souvenir.jumlah_stok -= new_jumlah
                new_souvenir.save()

        return instance
    
    # override method
    def create(self, validated_data):
        today = timezone.now().date()
        month = today.month
        year = today.year
        month_roman = int_to_roman(month)

        # Hitung jumlah SPK yang sudah ada
        existing_count = Survei.objects.filter(
            tanggal_spk__year=year,
            tanggal_spk__month=month
        ).count()

        # Format nomor SPK
        next_number = existing_count + 1
        formatted_number = f"{next_number:03d}"
        nomor_spk = f"{formatted_number}/SPK/{month_roman}/{year}"
        validated_data['nomor_spk'] = nomor_spk

        # Fallback tanggal_spk
        if not validated_data.get('tanggal_spk'):
            validated_data['tanggal_spk'] = today

        # Harga terbilang otomatis
        harga = validated_data.get('harga_survei')
        if harga:
            terbilang = num2words(int(harga), lang='id').title() + " Rupiah"
            validated_data['harga_survei_terbilang'] = terbilang

        # Handle stok souvenir
        souvenir = validated_data.get('souvenir')
        jumlah_souvenir = validated_data.get('jumlah_souvenir', 0)

        instance = super().create(validated_data)

        if souvenir and jumlah_souvenir:
            souvenir.jumlah_stok -= jumlah_souvenir
            souvenir.save()

        return instance


class SouvenirSerializer(serializers.ModelSerializer):
    out_of_stock = serializers.SerializerMethodField()

    class Meta:
        model = Souvenir
        fields = [
            'id',
            'nama_souvenir',
            'jumlah_stok',
            'jumlah_minimum',
            'out_of_stock'
        ]

    def get_out_of_stock(self, obj):
        if obj.jumlah_stok is None or obj.jumlah_minimum is None:
            return True
        return obj.jumlah_stok < obj.jumlah_minimum


class SurveiSouvenirCountSerializer(serializers.Serializer):
    souvenir_id = serializers.IntegerField()
    souvenir_name = serializers.CharField()
    count = serializers.IntegerField()
    jumlah_stok = serializers.IntegerField(required=False)
    jumlah_minimum = serializers.IntegerField(required=False)

class JumlahRespondenSerializer(serializers.ModelSerializer):
    class Meta:
        model = JumlahResponden
        fields = ['jumlah', 'updated_at']

# Tambahan helper function roman number
def int_to_roman(month):
    romans = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
    return romans[month - 1]
