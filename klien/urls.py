from django.urls import path
from . import views

# Nama aplikasi untuk namespacing, ini adalah praktik yang baik
app_name = 'klien'

urlpatterns = [
    # Endpoint untuk mendapatkan daftar semua klien (GET)
    # Sesuai dengan fetchKliens di FE
    path('', views.klien_list, name='klien_list'),

    # Endpoint untuk membuat klien baru (POST)
    # Sesuai dengan handleSubmit di FE TambahKlien
    path('create/', views.klien_create, name='klien_create'),

    # Endpoint untuk mendapatkan detail satu klien (GET)
    # Sesuai dengan handleDetail di FE
    path('<int:id>/', views.klien_detail, name='klien_detail'),

    # Endpoint untuk memperbarui data klien (POST/PUT)
    # Sesuai dengan handleUpdate di FE
    path('<int:id>/update/', views.klien_update, name='klien_update'),

    # Endpoint untuk menghapus klien (soft delete) (DELETE)
    # Sesuai dengan handleDelete di FE
    path('<int:id>/delete/', views.klien_delete, name='klien_delete'),

    # Endpoint untuk mendapatkan informasi detail file (nama, ukuran, url, dll) (GET)
    # Sesuai dengan fetchKlienFiles di FE
    path('<int:id>/dokumen-info/', views.dokumen_info, name='dokumen_info'),

    # Endpoint untuk mengunduh atau melihat pratinjau file (GET)
    # Sesuai dengan URL yang didapat dari `dokumen-info` dan digunakan oleh handleDownloadFile/handlePreviewFile
    path('<int:id>/download-dokumen/', views.download_dokumen, name='download_dokumen'),
    
    # Endpoint untuk menghapus dokumen spesifik (opsional jika dibutuhkan di masa depan)
    # path('<int:id>/delete-dokumen/', views.delete_dokumen, name='delete_dokumen'),
]