from rest_framework import serializers
from .models import Contract,Clause

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['id','vendor_name','risk_score','upload_at']

class ClauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clause
        fields = ['id','contract','clause_type','extracted_text']