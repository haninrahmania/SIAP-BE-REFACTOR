from django.urls import path
from .views import generate_invoice_dp, generate_invoice_final, download_template_proposal, upload_template_proposal, download_template_kontrak, upload_template_kontrak, generate_kwitansi_dp, generate_kwitansi_final, export_existing_invoice_dp, export_existing_invoice_final, export_existing_kwitansi_dp, export_existing_kwitansi_final, list_template_proposals, get_proposal_template_history, convert_pptx_to_image, delete_template_proposal_by_id, delete_kontrak_template, get_kontrak_template_history, generate_bast, export_existing_bast

urlpatterns = [
    path('generate_invoice_dp/', generate_invoice_dp, name='generate_invoice_dp'),
    path('generate_invoice_final/', generate_invoice_final, name='generate_invoice_final'),
    path('download_template_proposal/', download_template_proposal, name='download_template_proposal'),
    path('generate-kwitansi-dp/', generate_kwitansi_dp, name='generate_kwitansi_dp'),
    path('generate-kwitansi-final/', generate_kwitansi_final, name='generate_kwitansi_final'),
    path('upload_template_proposal/', upload_template_proposal, name='upload_template_proposal'),
    path('download_template_kontrak/', download_template_kontrak, name='download_template_kontrak'),
    path('upload_template_kontrak/', upload_template_kontrak, name='upload_template_kontrak'),
    path('get_kontrak_template_history/', get_kontrak_template_history, name='get_kontrak_template_history'),
    path('delete_kontrak_template/<int:id>/', delete_kontrak_template, name='delete_kontrak_template'),
    path('export_existing_invoice_dp/', export_existing_invoice_dp, name='export_existing_invoice_dp'),
    path('export_existing_invoice_final/', export_existing_invoice_final, name='export_existing_invoice_final'),
    path('export_existing_kwitansi_dp/', export_existing_kwitansi_dp, name='export_existing_kwitansi_dp'),
    path('export_existing_kwitansi_final/', export_existing_kwitansi_final, name='export_existing_kwitansi_final'),
    path('list_template_proposals/', list_template_proposals, name='list_template_proposals'),
    path('get_proposal_template_history/', get_proposal_template_history, name='get_proposal_template_history'),
    path('convert_pptx_to_image/', convert_pptx_to_image, name='convert_pptx_to_image'),
    path('delete_template_proposal_by_id/<int:id>/', delete_template_proposal_by_id, name='delete_template_proposal_by_id'),
    path('generate_bast/', generate_bast, name='generate_bast'),
    path('export_existing_bast/', export_existing_bast, name='export_existing_bast'),

]
