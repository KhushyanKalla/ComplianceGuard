from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Contract(models.Model):
    vendor_name = models.CharField(max_length=255)
    risk_score = models.IntegerField(default=0)
    upload_at = models.DateField(auto_now_add=True)
    ai_summary = models.TextField(blank=True,default="")
    
    
    def __str__(self):
        return f"{self.vendor_name} - risk {self.risk_score}"


class Clause(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='clauses',null=True)
    clause_type = models.CharField(max_length=100)
    extracted_text = models.TextField()
    def __str__(self):
        return f"{self.clause_type} for {self.contract.vendor_name}"

class ComplianceReport(models.Model):
    report_name = models.CharField(max_length=255)
    contract = models.ForeignKey(Contract,on_delete=models.CASCADE,related_name="reports",null=True)
    generated_at = models.DateField(auto_now_add=True)
    DECISION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    final_decision = models.CharField(choices=DECISION_CHOICES,default='approved',max_length=20)
    def __str__(self):
        return f"{self.report_name} - Status: {self.final_decision}"