from github import logger
from rest_framework.response import Response
from rest_framework.decorators import api_view, action, parser_classes

# from survei.signals import push_province_counts
from .models import Survei, DataKlien, Souvenir
from .serializers import SurveiPost, DataKlienSerializer, SouvenirSerializer, SurveiGet
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from collections import defaultdict
from rest_framework.parsers import MultiPartParser
import os
from django.conf import settings
from django.db.models import Count
from django.utils import timezone

class SurveiViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'])
    def init_data(self, request):
        klien_qs = DataKlien.objects.filter(is_deleted=False)
        klien_serialized = DataKlienSerializer(klien_qs, many=True).data

        souvenir_qs = Souvenir.objects.filter(is_deleted=False)
        souvenir_serialized = SouvenirSerializer(souvenir_qs, many=True).data

        return Response({
            "klien_list": klien_serialized,
            "souvenir_list": souvenir_serialized
        })

class SurveiPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100  

@api_view(['GET'])
def get_list_survei(request):
    paginator = SurveiPagination()
    survei = Survei.objects.all()
    result_page = paginator.paginate_queryset(survei, request)
    
    # GANTI DI SINI:
    serializer = SurveiGet(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def get_survei_detail(request, id):
    try:
        survei = Survei.objects.get(id=id)
    except Survei.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SurveiGet(survei)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_survei(request):
    serializer = SurveiPost(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()

        # try:
        #     push_counts_to_external_repo()  
        # except Exception as e:
        # # log but don’t 500 your API
        #     logger.error("Failed pushing CSV after creating Survei: %s", e)

        return Response(SurveiPost(instance).data, status=201)
    print("ERROR ADD SURVEI:", serializer.errors)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_ktp(request):
    ktp_file = request.FILES.get('ktp')
    if not ktp_file:
        return Response({'error': 'File KTP tidak ditemukan'}, status=status.HTTP_400_BAD_REQUEST)

    # Simpan file ke folder media/ktp_ppk
    folder_name = 'ktp_ppk'
    os.makedirs(os.path.join(settings.MEDIA_ROOT, folder_name), exist_ok=True)
    file_path = os.path.join(folder_name, ktp_file.name)
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    with open(full_path, 'wb+') as destination:
        for chunk in ktp_file.chunks():
            destination.write(chunk)

    # URL untuk diakses oleh frontend
    file_url = settings.MEDIA_URL + file_path
    return Response({'ktp_url': file_url}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
def update_survei(request, id):
    try:
        survei = Survei.objects.get(id=id)
    except Survei.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SurveiPost(survei, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_survei(request, id):
    try:
        survei = Survei.objects.get(id=id)
    except Survei.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    survei.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def survei_init_data(request):
    klien_queryset = DataKlien.objects.filter(is_deleted=False)
    klien_serialized = DataKlienSerializer(klien_queryset, many=True).data
    return Response({
        "klien_list": klien_serialized
    })

@api_view(['GET'])
def get_survei_count_by_souvenir(request):
    survei_with_souvenir = Survei.objects.exclude(souvenir=None)
    souvenir_counts = defaultdict(int)

    for survei in survei_with_souvenir:
        if survei.souvenir:
            souvenir_id = survei.souvenir.id
            souvenir_counts[souvenir_id] += 1

    # Ambil nama souvenir berdasarkan ID
    souvenir_names = Souvenir.objects.in_bulk(souvenir_counts.keys())

    # Format data untuk frontend (misalnya untuk chart atau tabel)
    data = [
        {
            "souvenir_id": sid,
            "souvenir_name": souvenir_names[sid].nama_souvenir if sid in souvenir_names else "Unknown",
            "count": count
        }
        for sid, count in souvenir_counts.items()
    ]

    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def survey_counts_by_province(request):
    today = timezone.localtime(timezone.now()).date()
    # Filter for Hanya Survei Sekarang
    if request.GET.get('status') == 'ongoing':
        qs = qs.filter(TanggalSelesai__gt=today)

    qs = (
        Survei.objects
              .values('wilayah_survei')                 # group by this field
              .annotate(count=Count('wilayah_survei'))  # count per group
    )
    data = [
        {"name": item["wilayah_survei"], "value": item["count"]}
        for item in qs
    ]

    # ---Datawrapper hanya bisa men-support dynamic endpoint, sehingga 
    # filter hanya bisa dipakai saat sudah di-deploy---

    # ---Return jika sudah deployed berupa Json Response---
    # data = [{'id': row['province__kode_provinsi'], 'value': row['value']}
    #         for row in qs]
    # return JsonResponse({'data': data})

    return Response(data)