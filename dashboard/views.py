from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from tracker_survei.models import TrackerSurvei

@api_view(['GET'])
def get_surveys_by_scope(request, scope):
    print("View berhasil dipanggil dengan scope:", scope)
    
    paginator = PageNumberPagination()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')


    # Ensure valid TrackerSurvei objects with related Survei
        # Fetch all TrackerSurvei objects with related Survei
    all_surveys = TrackerSurvei.objects.select_related('survei').all()

    if start_date:
        all_surveys = all_surveys.filter(survei__waktu_mulai_survei__gte=start_date)
    if end_date:
        all_surveys = all_surveys.filter(survei__waktu_mulai_survei__lte=end_date)

    # Manual filtering based on scope
    surveys = []
    for tracker in all_surveys:
        if tracker.survei:
            if scope == 'nasional' and tracker.survei.ruang_lingkup == 'Nasional':
                surveys.append(tracker)
            elif scope == 'provinsi' and tracker.survei.ruang_lingkup == 'Provinsi':
                surveys.append(tracker)
            elif scope == "kabupaten-kota" and tracker.survei.ruang_lingkup == 'Kabupaten/Kota':
                surveys.append(tracker)
            elif scope == 'keseluruhan':
                surveys.append(tracker)

    if not surveys:
        return JsonResponse({'error': 'No surveys found for the given scope'}, status=404)

 


    # Construct the data to return
    data = []
    for tracker in surveys:
        survey = tracker.survei
        survey_data = {
            'id': tracker.id,
            'nama_survei': survey.judul_survei,
            'waktu_mulai_survei': survey.tanggal_spk,
            'waktu_berakhir_survei': survey.tanggal_selesai,
            'klien': survey.klien.nama_perusahaan,
            'harga_survei': survey.harga_survei,
            'ruang_lingkup': survey.ruang_lingkup,
            'wilayah_survei': survey.wilayah_survei,
            'jumlah_responden': survey.jumlah_responden,
            'tipe_survei': survey.tipe_survei,
            'last_status': tracker.last_status,
        }
        data.append(survey_data)

    # Return paginated response
    return Response(data)


