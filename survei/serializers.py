import datetime
from rest_framework import serializers
from .models import Survei
from klien.models import DataKlien
from souvenir.models import Souvenir

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

    class Meta:
        model = Survei
        fields = (
            'id', 'judul_survei', 'nama_klien', 'jenis_survei',
            'ruang_lingkup', 'wilayah_survei', 'wilayah_survei_names',
            'tipe_survei', 'jumlah_responden', 'harga_survei',
            'tanggal_spk', 'tanggal_ws', 'tanggal_selesai',
            'milestone_1', 'milestone_2', 'milestone_3',
            'souvenir', 'ppk', 'peneliti'
        )

    def get_nama_klien(self, obj):
        if obj.klien:
            return f"{obj.klien.nama_perusahaan} - {obj.klien.nama_klien}"
        return "-"

    def get_wilayah_survei_names(self, obj):
        if obj.wilayah_survei:
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
            'souvenir', 'ppk', 'peneliti'
        )

    def get_nama_klien(self, obj):
        if obj.klien:
            return DataKlienSerializer(obj.klien).data.get("display_name")
        return None

    def get_wilayah_survei_names(self, obj):
        if obj.wilayah_survei:
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

    def create(self, validated_data):
        wilayah_data = validated_data.pop('wilayah_survei', [])
        validated_data['wilayah_survei'] = ", ".join(w['name'] for w in wilayah_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        wilayah_data = validated_data.pop('wilayah_survei', None)
        if wilayah_data is not None:
            validated_data['wilayah_survei'] = ", ".join(w['name'] for w in wilayah_data)
        return super().update(instance, validated_data)


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
