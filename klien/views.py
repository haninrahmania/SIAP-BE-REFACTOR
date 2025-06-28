from django.http import FileResponse, JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .models import DataKlien 
from .forms import DataKlienForm 
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q 
from django.core.files.storage import default_storage
from urllib.parse import quote
import json
import os
import re
import mimetypes
import logging

# Set up logging
logger = logging.getLogger(__name__)

# --- FUNGSI HELPER UNTUK FILE ---

def sanitize_filename(text):
    """Membersihkan teks agar aman digunakan sebagai nama file."""
    if not text:
        return ""
    # Hapus karakter spesial selain huruf, angka, spasi, dan tanda hubung
    sanitized = re.sub(r'[^\w\s-]', '', text)
    # Ganti spasi dengan garis bawah
    sanitized = re.sub(r'[\s_]+', '_', sanitized)
    # Hapus garis bawah di awal/akhir
    return sanitized.strip('_')

def generate_custom_filename(nama_klien, nama_perusahaan, original_filename):
    """Membuat nama file kustom yang unik."""
    _, ext = os.path.splitext(original_filename)
    
    clean_nama_klien = sanitize_filename(nama_klien)
    clean_nama_perusahaan = sanitize_filename(nama_perusahaan)
    
    if clean_nama_klien and clean_nama_perusahaan:
        base_name = f"{clean_nama_klien}_{clean_nama_perusahaan}"
    elif clean_nama_klien:
        base_name = clean_nama_klien
    elif clean_nama_perusahaan:
        base_name = clean_nama_perusahaan
    else:
        # Fallback jika tidak ada nama klien/perusahaan
        base_name, _ = os.path.splitext(original_filename)

    return f"{base_name}{ext}"

def get_client_file_path_prefix(klien_id):
    """Mengembalikan path prefix direktori file untuk klien."""
    return f'dokumen_klien/{klien_id}/'

def handle_single_file_upload(post_data, files_data):
    """
    Menangani upload satu file. Mengambil file dari request.FILES
    dan memberinya nama kustom.
    """
    # Nama field 'dokumen' harus cocok dengan yang dikirim dari Frontend (FormData)
    dokumen_field_name = 'dokumen'
    
    if dokumen_field_name in files_data:
        uploaded_file = files_data[dokumen_field_name]
        logger.info(f"File ditemukan: {uploaded_file.name} (size: {uploaded_file.size} bytes)")
        
        nama_klien = post_data.get('nama_klien', '')
        nama_perusahaan = post_data.get('nama_perusahaan', '')
        
        custom_filename = generate_custom_filename(nama_klien, nama_perusahaan, uploaded_file.name)
        uploaded_file.name = custom_filename
        
        logger.info(f"Nama file kustom dibuat: {custom_filename}")
        return uploaded_file
    
    logger.warning("Tidak ada file yang ditemukan di request.FILES dengan field 'dokumen'")
    return None

def save_file(klien_instance, uploaded_file):
    """Menyimpan satu file ke storage dan mengembalikan path-nya."""
    if not uploaded_file:
        return None
    
    # Hapus file lama jika ada untuk memastikan hanya ada satu file
    delete_existing_files(klien_instance.id)

    target_path = os.path.join(get_client_file_path_prefix(klien_instance.id), uploaded_file.name)
    
    try:
        saved_path = default_storage.save(target_path, uploaded_file)
        logger.info(f"File berhasil disimpan di: {saved_path}")
        return saved_path
    except Exception as e:
        logger.error(f"Gagal menyimpan file {uploaded_file.name} untuk klien {klien_instance.id}: {e}", exc_info=True)
        return None

def delete_existing_files(klien_id):
    """Menghapus semua file yang ada di direktori klien."""
    dir_prefix = get_client_file_path_prefix(klien_id)
    if default_storage.exists(dir_prefix):
        dirs, filenames = default_storage.listdir(dir_prefix)
        for filename in filenames:
            path_to_delete = os.path.join(dir_prefix, filename)
            default_storage.delete(path_to_delete)
            logger.info(f"File lama dihapus: {path_to_delete}")

def get_klien_file_info(klien_instance):
    """
    Mendapatkan informasi file tunggal yang terkait dengan klien.
    Mengembalikan dict jika file ditemukan, selain itu None.
    """
    dir_prefix = get_client_file_path_prefix(klien_instance.id)
    
    try:
        if default_storage.exists(dir_prefix):
            dirs, filenames = default_storage.listdir(dir_prefix)
            if filenames:
                # Ambil file pertama yang ditemukan
                filename = filenames[0]
                file_storage_path = os.path.join(dir_prefix, filename)
                
                # Buat URL untuk download dan preview
                base_endpoint = f"klien/{klien_instance.id}/download-dokumen/"
                
                return {
                    'path': file_storage_path,
                    'name': filename,
                    'file_exists': True,
                    'download_url': f"{base_endpoint}",
                    'preview_url': f"{base_endpoint}?preview=true",
                }
    except Exception as e:
        logger.warning(f"Tidak dapat listing file untuk klien {klien_instance.id}: {e}", exc_info=True)
    
    return None


# --- VIEWS (ENDPOINT API) ---

@csrf_exempt
def klien_list(request):
    """List semua klien dengan paginasi dan info dokumen."""
    if request.method == 'GET':
        page_number = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)
        search_query = request.GET.get('search', '')

        kliens = DataKlien.objects.filter(is_deleted=False).order_by('nama_klien')
        
        if search_query:
            kliens = kliens.filter(
                Q(nama_klien__icontains=search_query) |
                Q(nama_perusahaan__icontains=search_query) |
                Q(daerah__icontains=search_query) |
                Q(kategori_klien__icontains=search_query) |
                Q(no_telp__icontains=search_query)
            )
        
        paginator = Paginator(kliens, page_size)
        page_obj = paginator.get_page(page_number)

        results = []
        for klien in page_obj.object_list:
            file_info = get_klien_file_info(klien)
            
            klien_data = {
                'id': klien.id,
                'nama_klien': klien.nama_klien,
                'nama_perusahaan': klien.nama_perusahaan,
                'daerah': klien.daerah,
                'kategori_klien': klien.kategori_klien,
                'no_telp': klien.no_telp,
                # Frontend akan menggunakan `jumlah_dokumen` untuk menampilkan tombol
                'jumlah_dokumen': 1 if file_info else 0,
            }
            results.append(klien_data)

        return JsonResponse({
            'results': results,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'total_items': paginator.count,
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def klien_create(request):
    """Membuat klien baru dan menyimpan satu file."""
    if request.method == 'POST':
        logger.info("=== KLIEN CREATE REQUEST ===")
        form = DataKlienForm(request.POST)
        
        if form.is_valid():
            klien = form.save()
            logger.info(f"Klien berhasil dibuat dengan ID: {klien.id}")

            uploaded_file = handle_single_file_upload(request.POST, request.FILES)
            if uploaded_file:
                save_file(klien, uploaded_file)
            
            return JsonResponse({
                'id': klien.id,
                'nama_klien': klien.nama_klien,
                'message': 'Klien berhasil dibuat'
            }, status=201)
        else:
            logger.error(f"Form validation failed: {form.errors.as_json()}")
            return JsonResponse({'error': 'Form validation failed', 'details': form.errors}, status=400)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def klien_detail(request, id):
    """Mendapatkan detail satu klien beserta info filenya."""
    klien = get_object_or_404(DataKlien, id=id, is_deleted=False)
    file_info = get_klien_file_info(klien)
    
    response_data = {
        'id': klien.id,
        'nama_klien': klien.nama_klien,
        'nama_perusahaan': klien.nama_perusahaan,
        'daerah': klien.daerah,
        'kategori_klien': klien.kategori_klien,
        'no_telp': klien.no_telp,
        'jumlah_dokumen': 1 if file_info else 0,
        'dokumen_info': file_info, # Mengirim info file lengkap
    }
    return JsonResponse(response_data)


@csrf_exempt
def klien_update(request, id):
    """Memperbarui klien dan menangani pembaruan file."""
    klien = get_object_or_404(DataKlien, id=id, is_deleted=False)
    
    if request.method in ['POST', 'PUT']:
        form = DataKlienForm(request.POST, instance=klien)
        if form.is_valid():
            klien = form.save()
            
            uploaded_file = handle_single_file_upload(request.POST, request.FILES)
            if uploaded_file:
                # Jika ada file baru, simpan (fungsi save_file akan menghapus yang lama)
                save_file(klien, uploaded_file)

            return JsonResponse({'id': klien.id, 'message': 'Klien berhasil diupdate'}, status=200)
        else:
            return JsonResponse({'error': 'Form validation failed', 'details': form.errors}, status=400)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def klien_delete(request, id):
    """Soft delete klien."""
    if request.method == 'DELETE':
        klien = get_object_or_404(DataKlien, id=id)
        klien.is_deleted = True
        klien.save()
        # Optional: Hapus juga file-filenya dari storage
        delete_existing_files(id)
        return JsonResponse({'message': 'Klien berhasil dihapus'}, status=200)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def download_dokumen(request, id):
    """Menyajikan satu file untuk diunduh atau dilihat."""
    klien = get_object_or_404(DataKlien, id=id, is_deleted=False)
    file_info = get_klien_file_info(klien)
    
    if not file_info:
        raise Http404("Dokumen tidak ditemukan untuk klien ini.")
    
    file_storage_path = file_info['path']
    filename = file_info['name']
    is_preview = request.GET.get('preview', 'false').lower() == 'true'

    content_type, _ = mimetypes.guess_type(file_storage_path)
    content_type = content_type or 'application/octet-stream'
    
    response = FileResponse(default_storage.open(file_storage_path, 'rb'), content_type=content_type)
    
    disposition = 'inline' if is_preview else 'attachment'
    response['Content-Disposition'] = f'{disposition}; filename*=UTF-8\'\'{quote(filename)}'
    
    logger.info(f"Menyajikan file '{filename}' dengan disposisi '{disposition}'")
    return response


@csrf_exempt
def dokumen_info(request, id):
    """Memberikan detail file untuk ditampilkan di modal frontend."""
    klien = get_object_or_404(DataKlien, id=id, is_deleted=False)
    file_info = get_klien_file_info(klien)
    
    if not file_info:
        return JsonResponse({'jumlah_dokumen': 0, 'file_details': []})
        
    file_storage_path = file_info['path']
    file_exists = file_info.get('file_exists', False)
    file_size = default_storage.size(file_storage_path) if file_exists else 0
    
    file_detail = {
        'filename': file_info['name'],
        'file_size': file_size,
        'file_exists': file_exists,
        'url': file_info.get('download_url'),
        'preview_url': file_info.get('preview_url')
    }
    
    return JsonResponse({
        'jumlah_dokumen': 1,
        'file_details': [file_detail] # Frontend mengharapkan sebuah array
    })