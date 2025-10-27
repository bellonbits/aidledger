from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CustomUser(models.Model):
    """Extended user model for authentication"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=[
        ('donor', 'Donor'),
        ('ngo', 'NGO'),
        ('admin', 'Admin')
    ], default='donor')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


class Donor(models.Model):
    """Model representing a donor who contributes funds"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    wallet_id = models.CharField(max_length=50, unique=True, help_text="Hedera wallet address")
    total_donated = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    class Meta:
        ordering = ['-created_at']


class NGO(models.Model):
    """Model representing a Non-Governmental Organization"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    region = models.CharField(max_length=100)
    wallet_id = models.CharField(max_length=50, unique=True, help_text="Hedera wallet address")
    description = models.TextField(blank=True)
    total_received = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} ({self.region})"
    
    class Meta:
        ordering = ['-created_at']


class Recipient(models.Model):
    """Model representing a beneficiary who receives aid"""
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    wallet_id = models.CharField(max_length=50, unique=True, help_text="Hedera wallet address")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} ({self.location})"
    
    class Meta:
        ordering = ['-created_at']


class Donation(models.Model):
    """Model representing a donation from donor to NGO"""
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name='received_donations')
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    txn_hash = models.CharField(max_length=100, unique=True, help_text="Hedera transaction hash")
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed')
    ], default='pending')
    
    def __str__(self):
        return f"Donation: {self.donor.name} → {self.ngo.name} ({self.amount} AID)"
    
    class Meta:
        ordering = ['-timestamp']


class Distribution(models.Model):
    """Model representing aid distribution from NGO to recipient"""
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name='distributions')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='received_distributions')
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    txn_hash = models.CharField(max_length=100, unique=True, help_text="Hedera transaction hash")
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed')
    ], default='pending')
    
    def __str__(self):
        return f"Distribution: {self.ngo.name} → {self.recipient.name} ({self.amount} AID)"
    
    class Meta:
        ordering = ['-timestamp']


class AidLedgerStats(models.Model):
    """Model to store aggregated statistics"""
    total_donations = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_distributions = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_donors = models.IntegerField(default=0)
    total_ngos = models.IntegerField(default=0)
    total_recipients = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Stats - Donations: {self.total_donations}, Distributions: {self.total_distributions}"
    
    class Meta:
        verbose_name = "AidLedger Statistics"
        verbose_name_plural = "AidLedger Statistics"