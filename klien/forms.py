from django import forms
from .models import DataKlien

class DataKlienForm(forms.ModelForm):
    class Meta:
        model = DataKlien
        fields = ['nama_klien', 'nama_perusahaan', 'daerah']
