from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Survei
from .serializers import SurveiPost, DataKlienSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from klien.models import DataKlien

class SurveiViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'])
    def init_data(self, request):
        klien_qs = DataKlien.objects.filter(is_deleted=False)
        klien_serialized = DataKlienSerializer(klien_qs, many=True).data

        # bisa tambahkan souvenir juga jika perlu
        return Response({
            "klien_list": klien_serialized,
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
    serializer = SurveiPost(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def get_survei_detail(request, id):
    try:
        survei = Survei.objects.get(id=id)
    except Survei.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SurveiPost(survei)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_survei(request):
    serializer = SurveiPost(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

# @api_view(['GET'])
# def get_survei_count_by_region(request):
#     ruang_lingkup = request.query_params.get('ruang_lingkup', None)

#     REGION_CODE_MAPPING = {
#         "Aceh": "ID.AC",
#         "Bali": "ID.BA",
#         "Banten": "ID.BT", 
#         "Bengkulu": "ID.BE",
#         "DKI Jakarta": "ID.JK",
#         "Gorontalo": "ID.GO",
#         "Jambi": "ID.JA",
#         "Jawa Barat": "ID.JR",
#         "Jawa Tengah": "ID.JT",
#         "Jawa Timur": "ID.JI",
#         "Kalimantan Barat": "ID.KB",
#         "Kalimantan Selatan": "ID.KS",
#         "Kalimantan Tengah": "ID.KT",
#         "Kalimantan Timur": "ID.KI",
#         "Kepulauan Bangka Belitung": "ID.BB",
#         "Kepulauan Riau": "ID.KR",
#         "Lampung": "ID.LA",
#         "Maluku": "ID.MA",
#         "Nusa Tenggara Barat": "ID.NB",
#         "Nusa Tenggara Timur": "ID.NT",
#         "Papua": "ID.PA",
#         "Papua Barat": "ID.IB",
#         "Riau": "ID.RI",
#         "Sulawesi Barat": "ID.SR",
#         "Sulawesi Selatan": "ID.SL",
#         "Sulawesi Tengah": "ID.ST",
#         "Sulawesi Tenggara": "ID.SG",
#         "Sulawesi Utara": "ID.SW",
#         "Sumatera Barat": "ID.SB",
#         "Sumatera Selatan": "ID.SE",
#         "Sumatera Utara": "ID.SU",
#         "Yogyakarta": "ID.YO",
#         "Maluku Utara": "ID.133"
#     }

#     # Expanded list of cities grouped by province
#     CITIES = [
#         # Jakarta
#         {"id": "ID.JK.01", "name": "Jakarta Pusat", "province": "Jakarta"},
#         {"id": "ID.JK.02", "name": "Jakarta Utara", "province": "Jakarta"},
#         {"id": "ID.JK.03", "name": "Jakarta Barat", "province": "Jakarta"},
#         {"id": "ID.JK.04", "name": "Jakarta Selatan", "province": "Jakarta"},
#         {"id": "ID.JK.05", "name": "Jakarta Timur", "province": "Jakarta"},
        
#         # Jawa Barat
#         {"id": "ID.JB.01", "name": "Bandung", "province": "Jawa Barat"},
#         {"id": "ID.JB.02", "name": "Bogor", "province": "Jawa Barat"},
#         {"id": "ID.JB.03", "name": "Bekasi", "province": "Jawa Barat"},
#         {"id": "ID.JB.04", "name": "Depok", "province": "Jawa Barat"},
#         {"id": "ID.JB.05", "name": "Cimahi", "province": "Jawa Barat"},
#         {"id": "ID.JB.06", "name": "Tasikmalaya", "province": "Jawa Barat"},
#         {"id": "ID.JB.07", "name": "Cirebon", "province": "Jawa Barat"},
        
#         # Jawa Tengah
#         {"id": "ID.JT.01", "name": "Semarang", "province": "Jawa Tengah"},
#         {"id": "ID.JT.02", "name": "Solo", "province": "Jawa Tengah"},
#         {"id": "ID.JT.03", "name": "Magelang", "province": "Jawa Tengah"},
#         {"id": "ID.JT.04", "name": "Pekalongan", "province": "Jawa Tengah"},
#         {"id": "ID.JT.05", "name": "Tegal", "province": "Jawa Tengah"},
        
#         # Jawa Timur
#         {"id": "ID.JI.01", "name": "Surabaya", "province": "Jawa Timur"},
#         {"id": "ID.JI.02", "name": "Malang", "province": "Jawa Timur"},
#         {"id": "ID.JI.03", "name": "Sidoarjo", "province": "Jawa Timur"},
#         {"id": "ID.JI.04", "name": "Gresik", "province": "Jawa Timur"},
#         {"id": "ID.JI.05", "name": "Mojokerto", "province": "Jawa Timur"},
#         {"id": "ID.JI.06", "name": "Kediri", "province": "Jawa Timur"},
        
#         # Yogyakarta
#         {"id": "ID.YO.01", "name": "Yogyakarta", "province": "Yogyakarta"},
#         {"id": "ID.YO.02", "name": "Sleman", "province": "Yogyakarta"},
#         {"id": "ID.YO.03", "name": "Bantul", "province": "Yogyakarta"},
        
#         # Banten
#         {"id": "ID.BT.01", "name": "Tangerang", "province": "Banten"},
#         {"id": "ID.BT.02", "name": "Tangerang Selatan", "province": "Banten"},
#         {"id": "ID.BT.03", "name": "Serang", "province": "Banten"},
#         {"id": "ID.BT.04", "name": "Cilegon", "province": "Banten"},
        
#         # Sumatera Utara
#         {"id": "ID.SU.01", "name": "Medan", "province": "Sumatera Utara"},
#         {"id": "ID.SU.02", "name": "Binjai", "province": "Sumatera Utara"},
#         {"id": "ID.SU.03", "name": "Pematangsiantar", "province": "Sumatera Utara"},
        
#         # Sumatera Selatan
#         {"id": "ID.SS.01", "name": "Palembang", "province": "Sumatera Selatan"},
#         {"id": "ID.SS.02", "name": "Prabumulih", "province": "Sumatera Selatan"},
        
#         # Bali
#         {"id": "ID.BA.01", "name": "Denpasar", "province": "Bali"},
#         {"id": "ID.BA.02", "name": "Badung", "province": "Bali"},
#         {"id": "ID.BA.03", "name": "Gianyar", "province": "Bali"},
#     ]

#     if ruang_lingkup == "Nasional":
#         data = [{
#             "id": "ID",
#             "name": "Indonesia",
#             "province": None,  # No province for national level
#             "type": "country"
#         }]
#         return Response(data, status=status.HTTP_200_OK)

#     elif ruang_lingkup == "Provinsi":
#         data = [
#             {
#                 "id": code,
#                 "name": name,
#                 "province": None,  # No parent province for provinces
#                 "type": "province"
#             }
#             for name, code in REGION_CODE_MAPPING.items()
#         ]
#         # Sort provinces alphabetically
#         data.sort(key=lambda x: x['name'])
#         return Response(data, status=status.HTTP_200_OK)

#     elif ruang_lingkup == "Kota":
#         # Sort cities alphabetically first by province, then by city name
#         sorted_cities = sorted(CITIES, key=lambda x: (x['province'], x['name']))
#         data = [
#             {
#                 "id": city["id"],
#                 "name": city["name"],
#                 "province": city["province"],
#                 "type": "city"
#             }
#             for city in sorted_cities
#         ]
#         return Response(data, status=status.HTTP_200_OK)

#     else:
#         return Response(
#             {"error": "Invalid ruang_lingkup parameter"},
#             status=status.HTTP_400_BAD_REQUEST
#         )
    
# @api_view(['GET'])
# def get_survei_count_dashboard(request):
    ruang_lingkup = request.query_params.get('ruang_lingkup', None)

    REGION_CODE_MAPPING = {
        "Aceh": "ID.AC",
        "Bali": "ID.BA",
        "Banten": "ID.BT", 
        "Bengkulu": "ID.BE",
        "DKI Jakarta": "ID.JK",
        "Gorontalo": "ID.GO",
        "Jambi": "ID.JA",
        "Jawa Barat": "ID.JR",
        "Jawa Tengah": "ID.JT",
        "Jawa Timur": "ID.JI",
        "Kalimantan Barat": "ID.KB",
        "Kalimantan Selatan": "ID.KS",
        "Kalimantan Tengah": "ID.KT",
        "Kalimantan Timur": "ID.KI",
        "Kepulauan Bangka Belitung": "ID.BB",
        "Kepulauan Riau": "ID.KR",
        "Lampung": "ID.LA",
        "Maluku": "ID.MA",
        "Nusa Tenggara Barat": "ID.NB",
        "Nusa Tenggara Timur": "ID.NT",
        "Papua": "ID.PA",
        "Papua Barat": "ID.IB",
        "Riau": "ID.RI",
        "Sulawesi Barat": "ID.SR",
        "Sulawesi Selatan": "ID.SL",
        "Sulawesi Tengah": "ID.ST",
        "Sulawesi Tenggara": "ID.SG",
        "Sulawesi Utara": "ID.SW",
        "Sumatera Barat": "ID.SB",
        "Sumatera Selatan": "ID.SE",
        "Sumatera Utara": "ID.SU",
        "Yogyakarta": "ID.YO",
        "Maluku Utara": "ID.133"
    }

    if ruang_lingkup not in ["Nasional", "Provinsi"]:
        return Response(
            {"error": "Invalid ruang_lingkup parameter. Must be 'Nasional' or 'Provinsi'"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if ruang_lingkup == "Nasional":
        # Count all national surveys
        count = Survei.objects.filter(ruang_lingkup="Nasional").count()
        data = [{"id": "ID", "value": count}]
        return Response(data, status=status.HTTP_200_OK)
    
    else:  # Provinsi
        # Get all provincial surveys
        provinsi_surveys = Survei.objects.filter(ruang_lingkup="Provinsi")
        
        # Initialize count dictionary for all regions
        region_counts = {code: 0 for code in REGION_CODE_MAPPING.values()}
        
        # Count occurrences of each province
        for survey in provinsi_surveys:
            # Split the wilayah_survei_names into individual provinces
            if survey.wilayah_survei:
                provinces = [p.strip() for p in survey.wilayah_survei.split(',')]
                for province in provinces:
                    if province in REGION_CODE_MAPPING:
                        region_code = REGION_CODE_MAPPING[province]
                        region_counts[region_code] += 1

        # Format data for AnyChart
        data = [{"id": region_id, "value": count} 
                for region_id, count in region_counts.items()]
        
        return Response(data, status=status.HTTP_200_OK)