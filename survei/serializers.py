from rest_framework import serializers
from .models import Survei
from klien.models import DataKlien
from souvenir.models import Souvenir

class DataKlienSerializer(serializers.ModelSerializer):
    """Used for populating searchable dropdown."""
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = DataKlien
        fields = ['id', 'nama_perusahaan', 'nama_klien', 'display_name']

    def get_display_name(self, obj):
        return f"{obj.nama_perusahaan} - {obj.nama_klien}"


class SurveiGet(serializers.ModelSerializer):
    nama_klien = serializers.SerializerMethodField()

    class Meta:
        model = Survei
        fields = [
            'id',
            'judul_survei',
            'nama_klien',
            'jenis_survei',
            'ruang_lingkup',
            'wilayah_survei',
            'tipe_survei',
            'jumlah_responden',
            'harga_survei',
            'tanggal_spk',
            'tanggal_ws',
            'tanggal_selesai',
            'milestone_1',
            'milestone_2',
            'milestone_3',
        ]

class SurveiPost(serializers.ModelSerializer):
    klien_id = serializers.PrimaryKeyRelatedField(
        queryset=DataKlien.objects.all(),
        source='klien',
        write_only=True
    )
    nama_klien = serializers.SerializerMethodField(read_only=True)

    wilayah_survei = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    wilayah_survei_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Survei
        fields = (
            'id', 'judul_survei', 'klien_id', 'nama_klien', 'jenis_survei',
            'ruang_lingkup', 'wilayah_survei', 'wilayah_survei_names',
            'tipe_survei', 'jumlah_responden', 'harga_survei',
            'tanggal_spk', 'tanggal_ws', 'tanggal_selesai',
            'milestone_1', 'milestone_2', 'milestone_3',
        )

    def get_nama_klien(self, obj):
        return str(obj.klien) if obj.klien else None

    def get_wilayah_survei_names(self, obj):
        return obj.wilayah_survei.split(", ") if obj.wilayah_survei else []

    def validate_wilayah_survei(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("wilayah_survei must be a list.")
        for item in value:
            if 'name' not in item:
                raise serializers.ValidationError("Each item must have a 'name' field.")
        return value

    def create(self, validated_data):
        wilayah_data = validated_data.pop('wilayah_survei', [])
        validated_data['wilayah_survei'] = ", ".join(w['name'] for w in wilayah_data)
        return super().create(validated_data)


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
            return True  # anggap out of stock kalau data tidak lengkap
        return obj.jumlah_stok < obj.jumlah_minimum
