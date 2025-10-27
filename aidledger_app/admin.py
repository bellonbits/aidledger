from django.contrib import admin
from .models import CustomUser, Donor, NGO, Recipient, Donation, Distribution, AidLedgerStats


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone_number', 'created_at']
    list_filter = ['user_type', 'created_at']
    search_fields = ['user__username', 'phone_number']

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'wallet_id', 'total_donated', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'wallet_id']
    readonly_fields = ['created_at']

@admin.register(NGO)
class NGOAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'wallet_id', 'total_received', 'created_at']
    list_filter = ['region', 'created_at']
    search_fields = ['name', 'region', 'wallet_id']
    readonly_fields = ['created_at']


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'wallet_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'location', 'wallet_id']
    readonly_fields = ['created_at']


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'ngo', 'amount', 'status', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['donor__name', 'ngo__name', 'txn_hash']
    readonly_fields = ['txn_hash', 'timestamp']
    raw_id_fields = ['donor', 'ngo']


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = ['ngo', 'recipient', 'amount', 'status', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['ngo__name', 'recipient__name', 'txn_hash']
    readonly_fields = ['txn_hash', 'timestamp']
    raw_id_fields = ['ngo', 'recipient']


@admin.register(AidLedgerStats)
class AidLedgerStatsAdmin(admin.ModelAdmin):
    list_display = [
        'total_donations', 'total_distributions', 
        'total_donors', 'total_ngos', 'total_recipients', 'last_updated'
    ]
    readonly_fields = ['last_updated']
