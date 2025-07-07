from rest_framework import serializers
from .models import Survei
from klien.models import DataKlien

class SurveiGet(serializers.ModelSerializer):
    nama_klien = serializers.CharField(source='klien.nama_perusahaan', read_only=True)

    class Meta:
        model = Survei
        fields = [
            'id',
            'nama_survei',
            'nama_klien',
            'waktu_mulai_survei',
            'waktu_berakhir_survei',
            'harga_survei',
            'ruang_lingkup',
            'wilayah_survei',
            'jumlah_responden',
            'tipe_survei'
        ]

class SurveiPost(serializers.ModelSerializer):
    klien_id = serializers.PrimaryKeyRelatedField(
        queryset=DataKlien.objects.all(),
        source='klien',
        write_only=True
    )
    nama_klien = serializers.SerializerMethodField()
    wilayah_survei = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    wilayah_survei_names = serializers.SerializerMethodField()

    class Meta:
        model = Survei
        fields = (
            "id", "nama_survei", "waktu_mulai_survei",
            "waktu_berakhir_survei", "klien_id", "nama_klien",
            "harga_survei", "ruang_lingkup", "wilayah_survei",
            "wilayah_survei_names", "jumlah_responden", "tipe_survei"
        )

    def get_nama_klien(self, obj):
        """Return nama_perusahaan from the related DataKlien model as nama_klien."""
        return obj.klien.nama_perusahaan if obj.klien else None

    def get_wilayah_survei_names(self, obj):
        """Concatenate wilayah_survei names as a comma-separated string."""
        return obj.wilayah_survei

    def validate_wilayah_survei(self, value):
        """Ensure wilayah_survei is a list of dictionaries."""
        if not isinstance(value, list):
            raise serializers.ValidationError("wilayah_survei must be a list of objects.")
        for item in value:
            if 'name' not in item:
                raise serializers.ValidationError("Each wilayah_survei object must have a 'name' field.")
        return value

    def create(self, validated_data):
        wilayah_survei = validated_data.pop('wilayah_survei', [])
        # Convert the wilayah_survei list into a string for saving
        validated_data['wilayah_survei'] = ", ".join([wilayah['name'] for wilayah in wilayah_survei])
        return super().create(validated_data)
