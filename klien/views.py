from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .models import DataKlien
from .forms import DataKlienForm
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q 
import json

# List all clients (GET)
@csrf_exempt
def klien_list(request):
    if request.method == 'GET':
        page_number = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)
        search_query = request.GET.get('search', '')

        # Base queryset
        kliens = DataKlien.objects.filter(is_deleted=False)
        
        # Apply search if query exists
        if search_query:
            kliens = kliens.filter(
                Q(nama_klien__icontains=search_query) |
                Q(nama_perusahaan__icontains=search_query) |
                Q(daerah__icontains=search_query)
            )
        
        # Order and get values
        kliens = kliens.values(
            'id', 'nama_klien', 'nama_perusahaan', 'daerah'
        ).order_by('nama_klien')
        
        paginator = Paginator(kliens, page_size)

        try:
            page_obj = paginator.page(page_number)
        except:
            page_obj = paginator.page(1)

        response_data = {
            'results': list(page_obj.object_list),
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
        
        return JsonResponse(response_data, safe=False)

# Create a new client (POST)
@csrf_exempt
def klien_create(request):
    if request.method == 'POST':
        try:
            # Load JSON data from request body
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        form = DataKlienForm(data)
        if form.is_valid():
            klien = form.save()
            return JsonResponse({
                'id': klien.id,
                'nama_klien': klien.nama_klien,
                'nama_perusahaan': klien.nama_perusahaan,
                'daerah': klien.daerah
            }, status=201)
        return JsonResponse(form.errors, status=400)

# Detail view of a client (GET)
@csrf_exempt
def klien_detail(request, id):
    if request.method == 'GET':
        klien = get_object_or_404(DataKlien, id=id, is_deleted=False)
        return JsonResponse({
            'id': klien.id,
            'nama_klien': klien.nama_klien,
            'nama_perusahaan': klien.nama_perusahaan,
            'daerah': klien.daerah
        })

# Update client details (PUT)
@csrf_exempt
def klien_update(request, id):
    klien = get_object_or_404(DataKlien, id=id, is_deleted=False)
    
    if request.method == 'PUT' or request.method == 'POST':  # You can use either PUT or POST
        try:
            # Load JSON data from request body
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        form = DataKlienForm(data, instance=klien)
        
        if form.is_valid():
            klien = form.save()
            return JsonResponse({
                'id': klien.id,
                'nama_klien': klien.nama_klien,
                'nama_perusahaan': klien.nama_perusahaan,
                'daerah': klien.daerah
            }, status=200)
        else:
            return JsonResponse(form.errors, status=400)
    
    # Return error if method is not allowed
    return JsonResponse({"error": "Method not allowed"}, status=405)

# Soft delete a client (DELETE)
@csrf_exempt
def klien_delete(request, id):
    klien = get_object_or_404(DataKlien, id=id)
    if request.method == 'DELETE':
        klien.is_deleted = True  # Mark as deleted
        klien.save()
        return JsonResponse({'message': 'Client deleted successfully'}, status=204)

@csrf_exempt
def search_klien(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = DataKlien.objects.filter(
            Q(nama_klien__icontains=query) |
            Q(nama_perusahaan__icontains=query) |
            Q(daerah__icontains=query),
            is_deleted=False  # Only search for non-deleted clients
        )


    # Create response data in JSON format
    data = [
        {
            'nama_klien': klien.nama_klien,
            'nama_perusahaan': klien.nama_perusahaan,
            'daerah': klien.daerah,
        }
        for klien in results
    ]

    return JsonResponse(data, safe=False)
