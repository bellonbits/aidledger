from rest_framework import serializers
from .models import Donor, NGO, Recipient, Donation, Distribution, AidLedgerStats


class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = ['id', 'name', 'email', 'wallet_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class NGOSerializer(serializers.ModelSerializer):
    class Meta:
        model = NGO
        fields = ['id', 'name', 'region', 'wallet_id', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = ['id', 'name', 'location', 'wallet_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source='donor.name', read_only=True)
    ngo_name = serializers.CharField(source='ngo.name', read_only=True)
    
    class Meta:
        model = Donation
        fields = [
            'id', 'donor', 'ngo', 'donor_name', 'ngo_name', 
            'amount', 'txn_hash', 'timestamp', 'status'
        ]
        read_only_fields = ['id', 'txn_hash', 'timestamp', 'status']


class DistributionSerializer(serializers.ModelSerializer):
    ngo_name = serializers.CharField(source='ngo.name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.name', read_only=True)
    
    class Meta:
        model = Distribution
        fields = [
            'id', 'ngo', 'recipient', 'ngo_name', 'recipient_name',
            'amount', 'txn_hash', 'timestamp', 'status'
        ]
        read_only_fields = ['id', 'txn_hash', 'timestamp', 'status']


class AidLedgerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AidLedgerStats
        fields = [
            'total_donations', 'total_distributions', 'total_donors',
            'total_ngos', 'total_recipients', 'last_updated'
        ]
        read_only_fields = ['last_updated']


class DonationCreateSerializer(serializers.Serializer):
    donor_id = serializers.IntegerField()
    ngo_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    def validate_donor_id(self, value):
        try:
            Donor.objects.get(id=value)
        except Donor.DoesNotExist:
            raise serializers.ValidationError("Donor not found")
        return value
    
    def validate_ngo_id(self, value):
        try:
            NGO.objects.get(id=value)
        except NGO.DoesNotExist:
            raise serializers.ValidationError("NGO not found")
        return value


class DistributionCreateSerializer(serializers.Serializer):
    ngo_id = serializers.IntegerField()
    recipient_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    def validate_ngo_id(self, value):
        try:
            NGO.objects.get(id=value)
        except NGO.DoesNotExist:
            raise serializers.ValidationError("NGO not found")
        return value
    
    def validate_recipient_id(self, value):
        try:
            Recipient.objects.get(id=value)
        except Recipient.DoesNotExist:
            raise serializers.ValidationError("Recipient not found")
        return value
