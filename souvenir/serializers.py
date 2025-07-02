from rest_framework import serializers
from .models import Souvenir

class SouvenirGet(serializers.ModelSerializer):
    class Meta:
        model = Souvenir
        fields = (
            "id",
            "nama_souvenir",
            "jumlah_stok",
            "jumlah_minimum",
            "kategori",
            "harga_per_pcs",
            "nama_vendor",
            "kontak_vendor",
            "tanggal_order",
            "tanggal_diterima",
        )

class SouvenirPost(serializers.ModelSerializer):
    class Meta:
        model = Souvenir
        fields = (
            "id",
            "nama_souvenir",
            "jumlah_stok",
            "jumlah_minimum",
            "kategori",
            "harga_per_pcs",
            "nama_vendor",
            "kontak_vendor",
            "tanggal_order",
            "tanggal_diterima",
        )
