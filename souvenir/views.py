from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Souvenir
from .serializers import SouvenirGet, SouvenirPost
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from urllib.parse import unquote


class SouvenirPagination(PageNumberPagination):
    page_size = 10  # Jumlah item per halaman
    page_size_query_param = 'page_size'  # Parameter untuk mengubah ukuran halaman
    max_page_size = 100  # Ukuran maksimum halaman


@api_view(['GET'])
def get_list_souvenir(request):
    paginator = SouvenirPagination()
    # Hanya ambil item yang belum dihapus
    souvenir = Souvenir.objects.filter(is_deleted=False).order_by("id")
    result_page = paginator.paginate_queryset(souvenir, request)
    serializer = SouvenirGet(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def get_souvenir_detail(request, id):
    try:
        # Hanya ambil item yang belum dihapus
        souvenir = Souvenir.objects.get(id=str(id), is_deleted=False)
    except Souvenir.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SouvenirGet(souvenir)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_souvenir(request):
    # Mengecek apakah nama souvenir sudah ada, baik yang aktif maupun yang soft deleted
    nama_souvenir = request.data.get('nama_souvenir')
    if Souvenir.objects.filter(nama_souvenir=nama_souvenir).exists():
        # Jika nama souvenir sudah ada, periksa apakah is_deleted True
        existing_souvenir = Souvenir.objects.filter(nama_souvenir=nama_souvenir).first()
        if existing_souvenir.is_deleted:
            # Jika sudah dihapus, biarkan tambah data baru
            serializer = SouvenirPost(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Jika tidak dihapus, beri tahu pengguna bahwa nama sudah terpakai
            return Response({"message": "Nama souvenir sudah ada."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Jika tidak ada, lanjutkan untuk menyimpan souvenir baru
    serializer = SouvenirPost(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        get_serializer = SouvenirGet(instance)
        return Response(get_serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_souvenir(request, id):
    try:
        # Hanya ambil item yang belum dihapus
        souvenir = Souvenir.objects.get(id=str(id), is_deleted=False)
    except Souvenir.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SouvenirPost(souvenir, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_souvenir(request, id):
    try:
        # Dapatkan souvenir yang belum dihapus
        souvenir = Souvenir.objects.get(id=str(id), is_deleted=False)
    except Souvenir.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Soft delete dengan mengubah `is_deleted` menjadi True
    souvenir.is_deleted = True
    souvenir.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def check_souvenir(request, nama_souvenir):
    try:
        decoded_nama = unquote(nama_souvenir).strip()
        print(f"Searching souvenir with name: '{decoded_nama}'")

        souvenir = Souvenir.objects.filter(nama_souvenir__iexact=decoded_nama).first()
        if souvenir is not None:
            return Response({
                'id': souvenir.id,
                'is_deleted': souvenir.is_deleted
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Souvenir tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)