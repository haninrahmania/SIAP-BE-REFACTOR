from django.http import JsonResponse
# from django.contrib.auth import get_user_model
from dokumen_pendukung.models import InvoiceDP, InvoiceFinal, KwitansiDP, KwitansiFinal, BAST
from django.shortcuts import get_object_or_404
# from .models import DaftarAkun
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.db.models.functions import Concat
from urllib.parse import unquote
import json

# List all documents (GET)
@csrf_exempt
def dokumen_list(request):

    # Query InvoiceDP
    invoice_dp = InvoiceDP.objects.filter(is_deleted=False).values(
        'id', 'client_name', 'survey_name', 'doc_type'
    )

    # Query InvoiceFinal
    invoice_final = InvoiceFinal.objects.filter(is_deleted=False).values(
        'id', 'client_name', 'survey_name', 'doc_type'
    )

    # Query KwitansiDP
    kwitansi_dp = KwitansiDP.objects.filter(is_deleted=False).values(
        'id', 'client_name', 'survey_name', 'doc_type'
    )

    # Query KwitansiFinal
    kwitansi_final = KwitansiFinal.objects.filter(is_deleted=False).values(
        'id', 'client_name', 'survey_name', 'doc_type'
    )

    # Query BAST
    bast = BAST.objects.values(
        'nomor', 'nama_pihak_kedua', 'judul_survei', 'doc_type'
    )

    if request.method == 'GET':
        dokumen = invoice_dp.union(invoice_final, kwitansi_dp, kwitansi_final, bast)
        dokumen_list = list(dokumen)
        return JsonResponse(dokumen_list, safe=False)

# # Get an existing account (GET)
# @csrf_exempt
# def get_existing_account(request):
#     if request.method == 'GET':
#         # Fetch all accounts that were created in a different page
#         # Modify the filter criteria as needed if you want specific accounts
#         dokumen = InvoiceDP.objects.filter(is_deleted=False).values('id','username', 'first_name', 'last_name', 'email', 'role')
#         dokumen_list = list(dokumen)
        
#         # Return the existing accounts in JSON format
#         return JsonResponse(dokumen_list, safe=False)
#     else:
#         return JsonResponse({"error": "Invalid request method"}, status=405)

# Endpoint delete di backend (soft delete)
@csrf_exempt
def dokumen_delete(request, id):
    decoded_id = unquote(id)
    # Attempt to find the document in one of the models
    dokumen = None
    try:
        dokumen = InvoiceDP.objects.get(id=decoded_id)
    except InvoiceDP.DoesNotExist:
        try:
            dokumen = InvoiceFinal.objects.get(id=decoded_id)
        except InvoiceFinal.DoesNotExist:
            try:
                dokumen = KwitansiDP.objects.get(id=decoded_id)
            except KwitansiDP.DoesNotExist:
                try:
                    dokumen = KwitansiFinal.objects.get(id=decoded_id)
                except KwitansiFinal.DoesNotExist:
                    return JsonResponse({'error': 'Document not found'}, status=404)

    if request.method == 'DELETE':
        dokumen.is_deleted =True  # Mark as deleted
        dokumen.save()
        return JsonResponse({'message': 'Document deleted successfully'}, status=204)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# Detail view of a document (GET)
@csrf_exempt
def dokumen_detail(request, id):
    decoded_id = unquote(id)
    print(f"Decoded ID: {decoded_id}")

    # Query InvoiceDP
    invoice_dp = InvoiceDP.objects.filter(is_deleted=False, id=decoded_id).values(
        'id', 'survey_name', 'client_name', 'doc_type',
        'respondent_count', 'address', 'amount', 
        'nominal_tertulis', 'paid_percentage', 'additional_info', 'date'
    ).first()

    # Query InvoiceFinal
    invoice_final = InvoiceFinal.objects.filter(is_deleted=False, id=decoded_id).values(
        'id', 'survey_name', 'client_name', 'doc_type',
        'respondent_count', 'address', 'amount', 
        'nominal_tertulis', 'paid_percentage', 'additional_info', 'date'
    ).first()

    # Query KwitansiDP
    kwitansi_dp = KwitansiDP.objects.filter(is_deleted=False, id=decoded_id).values(
        'id', 'survey_name', 'client_name', 'doc_type', 
        'amount', 'nominal_tertulis', 'additional_info', 'date'
    ).first()

    # Query KwitansiFinal
    kwitansi_final = KwitansiFinal.objects.filter(is_deleted=False, id=decoded_id).values(
        'id', 'survey_name', 'client_name', 'doc_type', 
        'amount', 'nominal_tertulis', 'additional_info', 'date'
    ).first()

    # Query BAST
    bast = BAST.objects.filter(nomor=decoded_id).values(
        'nomor', 'nama_pihak_pertama', 'jabatan_pihak_pertama', 
        'tanggal_tertulis', 'tanggal', 'alamat_pihak_pertama',
        'tanggal', 'judul_survei', 'nomor_addendum', 'tanggal_addendum',
        'nilai_kontrak_angka', 'nilai_kontrak_tertulis', 'doc_type',
        'nama_pihak_kedua', 'jabatan_pihak_kedua', 'alamat_pihak_kedua',
        'created_at', 'nomor_spk', 'tanggal_spk'
    ).first()

    if request.method == 'GET':
        dokumen = invoice_dp or invoice_final or kwitansi_dp or kwitansi_final or bast
        if dokumen:
            return JsonResponse(dokumen, safe=False)
        else:
            return JsonResponse({'error': 'Document not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


# Search documents
@csrf_exempt
def search_dokumen(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        # Query InvoiceDP
        invoice_dp_results = InvoiceDP.objects.filter(
            Q(id__icontains=query) |
            Q(survey_name__icontains=query) |
            Q(client_name__icontains=query) |
            Q(doc_type__icontains=query),
            is_deleted=False
        ).values('id', 'survey_name', 'client_name', 'doc_type')

        # Query InvoiceFinal
        invoice_final_results = InvoiceFinal.objects.filter(
            Q(id__icontains=query) |
            Q(survey_name__icontains=query) |
            Q(client_name__icontains=query) |
            Q(doc_type__icontains=query),
            is_deleted=False
        ).values('id', 'survey_name', 'client_name', 'doc_type')

        # Query KwitansiDP
        kwitansi_dp_results = KwitansiDP.objects.filter(
            Q(id__icontains=query) |
            Q(survey_name__icontains=query) |
            Q(client_name__icontains=query) |
            Q(doc_type__icontains=query),
            is_deleted=False
        ).values('id', 'survey_name', 'client_name', 'doc_type')

        # Query KwitansiFinal
        kwitansi_final_results = KwitansiFinal.objects.filter(
            Q(id__icontains=query) |
            Q(survey_name__icontains=query) |
            Q(client_name__icontains=query) |
            Q(doc_type__icontains=query),
            is_deleted=False
        ).values('id', 'survey_name', 'client_name', 'doc_type')

        # Query BAST
        bast_results = BAST.objects.filter(
            Q(nomor__icontains=query) |
            Q(nama_pihak_pertama__icontains=query) |
            Q(jabatan_pihak_pertama__icontains=query) |
            Q(tanggal_tertulis__icontains=query) |
            Q(tanggal__icontains=query) |
            Q(alamat_pihak_pertama__icontains=query) |
            Q(tanggal__icontains=query) |
            Q(judul_survei__icontains=query) |
            Q(nomor_addendum__icontains=query) |
            Q(tanggal_addendum__icontains=query) |
            Q(nilai_kontrak_angka__icontains=query) |
            Q(nilai_kontrak_tertulis__icontains=query) |
            Q(doc_type__icontains=query) |
            Q(nama_pihak_kedua__icontains=query) |
            Q(jabatan_pihak_kedua__icontains=query) |
            Q(alamat_pihak_kedua__icontains=query) |
            Q(created_at__icontains=query) |
            Q(nomor_spk__icontains=query) |
            Q(tanggal_spk__icontains=query),
        ).values(
            'nomor', 'nama_pihak_pertama', 'jabatan_pihak_pertama', 
            'tanggal_tertulis', 'tanggal', 'alamat_pihak_pertama',
            'tanggal', 'judul_survei', 'nomor_addendum', 'tanggal_addendum',
            'nilai_kontrak_angka', 'nilai_kontrak_tertulis', 'doc_type',
            'nama_pihak_kedua', 'jabatan_pihak_kedua', 'alamat_pihak_kedua',
            'created_at', 'nomor_spk', 'tanggal_spk'
        )

    # Combine results using union
    combined_results = invoice_dp_results.union(invoice_final_results, kwitansi_dp_results, kwitansi_final_results, bast_results)

    # Structure the data
    data = [
        {
            'id': dokumen['id'] if 'id' in dokumen else dokumen['nomor'],
            'survey_name': dokumen['survey_name'] if 'survey_name' in dokumen else dokumen['judul_survei'],
            'client_name': dokumen['client_name'] if 'client_name' in dokumen else dokumen['nama_pihak_kedua'],
            'doc_type': dokumen['doc_type'],
        }
        for dokumen in combined_results
    ]

    return JsonResponse(data, safe=False)
