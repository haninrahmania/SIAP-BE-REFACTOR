from rest_framework import serializers
from .models import Souvenir

class SouvenirGet(serializers.ModelSerializer):
    class Meta:
        model = Souvenir
        fields = ("id","nama_souvenir","jumlah_stok","jumlah_minimum")

class SouvenirPost(serializers.ModelSerializer):
    class Meta:
        model = Souvenir
        fields = ("id","nama_souvenir","jumlah_stok","jumlah_minimum")