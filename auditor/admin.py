from django.contrib import admin
from .models import Contract,ComplianceReport,Clause 
# Register your models here.
@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor_name', 'risk_score', 'upload_at')
    search_fields = ('vendor_name',)
    
@admin.register(Clause)
class ClauseAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract', 'clause_type')
    search_fields = ('clause_type',)
    
@admin.register(ComplianceReport)
class ComplianceReporAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_name', 'final_decision')
    list_filter = ('final_decision',)