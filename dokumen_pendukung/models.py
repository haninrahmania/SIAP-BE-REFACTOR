from django.db import models

class KontrakTemplateHistory(models.Model):
    file = models.FileField(upload_to='templates/kontrak/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"TemplateKontrak v{self.id} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
class TemplateProposal(models.Model):
    nama_file = models.CharField(max_length=255)
    file = models.FileField(upload_to='template_proposals/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_file
    
class ProposalTemplateHistory(models.Model):
    file = models.FileField(upload_to='unused_path/', blank=True)  # tidak akan dipakai
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Template {self.id} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

class InvoiceDP(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    client_name = models.CharField(max_length=255)
    survey_name = models.CharField(max_length=255)
    respondent_count = models.IntegerField()
    address = models.TextField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    nominal_tertulis = models.TextField()
    paid_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    additional_info = models.TextField(blank=True, null=True)
    date = models.DateField()
    doc_type = models.CharField(max_length=50, default="invoiceDP")  # Added max_length
    is_deleted = models.BooleanField(default=False)
    beneficiary_bank_name = models.CharField(max_length=255, blank=True, null=True)
    beneficiary_account_name = models.CharField(max_length=255, blank=True, null=True)
    beneficiary_account_number = models.CharField(max_length=100, blank=True, null=True)
    account_currency = models.CharField(max_length=50, blank=True, null=True)
    beneficiary_bank_address = models.TextField(blank=True, null=True)
    beneficiary_swift_code = models.CharField(max_length=20, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.client_name} - {self.survey_name}"

class InvoiceFinal(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    client_name = models.CharField(max_length=255)
    survey_name = models.CharField(max_length=255)
    respondent_count = models.IntegerField()
    address = models.TextField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    nominal_tertulis = models.TextField()
    paid_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    additional_info = models.TextField(blank=True, null=True)
    date = models.DateField()
    doc_type = models.CharField(max_length=50, default="invoiceFinal")  # Added max_length
    is_deleted = models.BooleanField(default=False)
    beneficiary_bank_name = models.CharField(max_length=255, blank=True, null=True)
    beneficiary_account_name = models.CharField(max_length=255, blank=True, null=True)
    beneficiary_account_number = models.CharField(max_length=100, blank=True, null=True)
    account_currency = models.CharField(max_length=50, blank=True, null=True)
    beneficiary_bank_address = models.TextField(blank=True, null=True)
    beneficiary_swift_code = models.CharField(max_length=20, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.client_name} - {self.survey_name}"

class KwitansiDP(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    client_name = models.CharField(max_length=255)
    survey_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    nominal_tertulis = models.TextField()
    additional_info = models.TextField(blank=True, null=True)
    date = models.DateField()
    doc_type = models.CharField(max_length=50, default="kwitansiDP")  # Added max_length
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client_name} - {self.survey_name}"

class KwitansiFinal(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    client_name = models.CharField(max_length=255)
    survey_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    nominal_tertulis = models.TextField()
    additional_info = models.TextField(blank=True, null=True)
    date = models.DateField()
    doc_type = models.CharField(max_length=50, default="kwitansiFinal")  # Added max_length
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client_name} - {self.survey_name}"
