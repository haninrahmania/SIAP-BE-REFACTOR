from rest_framework import serializers
from .models import TemplateProposal, ProposalTemplateHistory

class TemplateProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateProposal
        fields = '__all__'

class ProposalTemplateHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalTemplateHistory
        fields = ['id', 'file', 'uploaded_at']