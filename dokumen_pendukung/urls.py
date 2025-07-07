from django.urls import path
from .views import generate_invoice_dp, generate_invoice_final, download_template_proposal, upload_template_proposal, download_template_kontrak, upload_template_kontrak, generate_kwitansi_dp, generate_kwitansi_final, export_existing_invoice_dp, export_existing_invoice_final, export_existing_kwitansi_dp, export_existing_kwitansi_final

urlpatterns = [
    path('generate_invoice_dp/', generate_invoice_dp, name='generate_invoice_dp'),
    path('generate_invoice_final/', generate_invoice_final, name='generate_invoice_final'),
    path('download_template_proposal/', download_template_proposal, name='download_template_proposal'),
    path('generate-kwitansi-dp/', generate_kwitansi_dp, name='generate_kwitansi_dp'),
    path('generate-kwitansi-final/', generate_kwitansi_final, name='generate_kwitansi_final'),
    path('upload_template_proposal/', upload_template_proposal, name='upload_template_proposal'),
    path('download_template_kontrak/', download_template_kontrak, name='download_template_kontrak'),
    path('upload_template_kontrak/', upload_template_kontrak, name='upload_template_kontrak'),
    path('export_existing_invoice_dp/', export_existing_invoice_dp, name='export_existing_invoice_dp'),
    path('export_existing_invoice_final/', export_existing_invoice_final, name='export_existing_invoice_final'),
    path('export_existing_kwitansi_dp/', export_existing_kwitansi_dp, name='export_existing_kwitansi_dp'),
    path('export_existing_kwitansi_final/', export_existing_kwitansi_final, name='export_existing_kwitansi_final'),
]