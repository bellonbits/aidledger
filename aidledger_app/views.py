from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from decimal import Decimal
import logging

from .models import CustomUser, Donor, NGO, Recipient, Donation, Distribution, AidLedgerStats
from .serializers import (
    DonorSerializer, NGOSerializer, RecipientSerializer,
    DonationSerializer, DistributionSerializer, AidLedgerStatsSerializer,
    DonationCreateSerializer, DistributionCreateSerializer
)
from .hedera_service import hedera_service

logger = logging.getLogger(__name__)


class DonorListCreateView(generics.ListCreateAPIView):
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer


class NGOListCreateView(generics.ListCreateAPIView):
    queryset = NGO.objects.all()
    serializer_class = NGOSerializer


class RecipientListCreateView(generics.ListCreateAPIView):
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer


class DonationListView(generics.ListAPIView):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer


class DistributionListView(generics.ListAPIView):
    queryset = Distribution.objects.all()
    serializer_class = DistributionSerializer


@api_view(['POST'])
def create_donation(request):
    """Create a new donation and log it to Hedera"""
    serializer = DonationCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            donor = Donor.objects.get(id=serializer.validated_data['donor_id'])
            ngo = NGO.objects.get(id=serializer.validated_data['ngo_id'])
            amount = serializer.validated_data['amount']
            
            # Log to Hedera HCS
            txn_hash = hedera_service.log_donation_to_hcs(
                donor.name, ngo.name, float(amount)
            )
            
            # Create donation record
            donation = Donation.objects.create(
                donor=donor,
                ngo=ngo,
                amount=amount,
                txn_hash=txn_hash,
                status='confirmed'
            )
            
            # Update donor and NGO totals
            donor.total_donated += amount
            donor.save()
            
            ngo.total_received += amount
            ngo.save()
            
            # Update statistics
            stats, created = AidLedgerStats.objects.get_or_create(
                defaults={'total_donations': 0, 'total_distributions': 0}
            )
            stats.total_donations += amount
            stats.save()
            
            response_serializer = DonationSerializer(donation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"Failed to create donation: {e}")
        return Response(
            {'error': 'Failed to create donation', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def create_distribution(request):
    """Create a new distribution and log it to Hedera"""
    serializer = DistributionCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            ngo = NGO.objects.get(id=serializer.validated_data['ngo_id'])
            recipient = Recipient.objects.get(id=serializer.validated_data['recipient_id'])
            amount = serializer.validated_data['amount']
            
            # Log to Hedera HCS
            txn_hash = hedera_service.log_distribution_to_hcs(
                ngo.name, recipient.name, float(amount)
            )
            
            # Create distribution record
            distribution = Distribution.objects.create(
                ngo=ngo,
                recipient=recipient,
                amount=amount,
                txn_hash=txn_hash,
                status='confirmed'
            )
            
            # Update statistics
            stats, created = AidLedgerStats.objects.get_or_create(
                defaults={'total_donations': 0, 'total_distributions': 0}
            )
            stats.total_distributions += amount
            stats.save()
            
            response_serializer = DistributionSerializer(distribution)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"Failed to create distribution: {e}")
        return Response(
            {'error': 'Failed to create distribution', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_transactions(request):
    """Get all transactions (donations and distributions)"""
    donations = Donation.objects.all()
    distributions = Distribution.objects.all()
    
    donation_data = DonationSerializer(donations, many=True).data
    distribution_data = DistributionSerializer(distributions, many=True).data
    
    return Response({
        'donations': donation_data,
        'distributions': distribution_data
    })


@api_view(['GET'])
def verify_transaction(request, txn_hash):
    """Verify a transaction using Hedera Mirror Node API"""
    try:
        verification_result = hedera_service.verify_transaction(txn_hash)
        return Response(verification_result)
    except Exception as e:
        logger.error(f"Failed to verify transaction {txn_hash}: {e}")
        return Response(
            {'error': 'Failed to verify transaction', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_stats(request):
    """Get AidLedger statistics"""
    stats, created = AidLedgerStats.objects.get_or_create(
        defaults={
            'total_donations': 0,
            'total_distributions': 0,
            'total_donors': Donor.objects.count(),
            'total_ngos': NGO.objects.count(),
            'total_recipients': Recipient.objects.count()
        }
    )
    
    # Update counts
    stats.total_donors = Donor.objects.count()
    stats.total_ngos = NGO.objects.count()
    stats.total_recipients = Recipient.objects.count()
    stats.save()
    
    serializer = AidLedgerStatsSerializer(stats)
    return Response(serializer.data)


# Authentication Views
def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type', 'donor')
        phone_number = request.POST.get('phone_number', '')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'registration/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'registration/register.html')
        
        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1
                )
                
                # Create CustomUser profile
                custom_user = CustomUser.objects.create(
                    user=user,
                    user_type=user_type,
                    phone_number=phone_number
                )
                
                # Create Donor or NGO profile
                if user_type == 'donor':
                    donor = Donor.objects.create(
                        user=user,
                        name=username,
                        email=email,
                        wallet_id=f"0.0.{user.id}0001"  # Simplified for demo
                    )
                elif user_type == 'ngo':
                    ngo = NGO.objects.create(
                        user=user,
                        name=username,
                        region="Global",
                        wallet_id=f"0.0.{user.id}0002",
                        description=f"NGO created by {username}"
                    )
                
                # Log the user in
                login(request, user)
                messages.success(request, f'Account created successfully! Welcome to AidLedger, {username}!')
                return redirect('user_dashboard')
                
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'registration/register.html')
    
    return render(request, 'registration/register.html')


def login_view(request):
    """Custom login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')


@login_required
def user_dashboard(request):
    """User-specific dashboard"""
    user = request.user
    context = {}
    
    try:
        custom_user = CustomUser.objects.get(user=user)
        
        if custom_user.user_type == 'donor':
            donor = Donor.objects.get(user=user)
            donations = Donation.objects.filter(donor=donor).order_by('-timestamp')[:10]
            
            # Get wallet balance
            try:
                balance = hedera_service.get_account_balance(donor.wallet_id)
            except:
                balance = {'hbar_balance': '0', 'token_balances': []}
            
            context.update({
                'profile': donor,
                'donations': donations,
                'user_type': 'donor',
                'balance': balance,
                'ngos': NGO.objects.all()  # For donation form
            })
            
        elif custom_user.user_type == 'ngo':
            ngo = NGO.objects.get(user=user)
            donations = Donation.objects.filter(ngo=ngo).order_by('-timestamp')[:10]
            distributions = Distribution.objects.filter(ngo=ngo).order_by('-timestamp')[:10]
            
            # Get wallet balance
            try:
                balance = hedera_service.get_account_balance(ngo.wallet_id)
            except:
                balance = {'hbar_balance': '0', 'token_balances': []}
            
            context.update({
                'profile': ngo,
                'donations': donations,
                'distributions': distributions,
                'user_type': 'ngo',
                'balance': balance,
                'recipients': Recipient.objects.all()  # For distribution form
            })
        
    except (CustomUser.DoesNotExist, Donor.DoesNotExist, NGO.DoesNotExist):
        messages.error(request, 'User profile not found.')
        return redirect('logout')
    
    return render(request, 'user_dashboard.html', context)


@login_required
def make_donation_view(request):
    """View for donors to make donations"""
    if not hasattr(request.user, 'customuser') or request.user.customuser.user_type != 'donor':
        messages.error(request, 'Only donors can make donations.')
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        ngo_id = request.POST.get('ngo_id')
        amount = request.POST.get('amount')
        
        try:
            donor = Donor.objects.get(user=request.user)
            ngo = NGO.objects.get(id=ngo_id)
            
            # Create donation directly instead of API call
            with transaction.atomic():
                # Log to Hedera HCS
                txn_hash = hedera_service.log_donation_to_hcs(
                    donor.name, ngo.name, float(amount)
                )
                
                # Create donation record
                donation = Donation.objects.create(
                    donor=donor,
                    ngo=ngo,
                    amount=amount,
                    txn_hash=txn_hash,
                    status='confirmed'
                )
                
                # Update donor and NGO totals
                donor.total_donated += Decimal(amount)
                donor.save()
                
                ngo.total_received += Decimal(amount)
                ngo.save()
                
                # Update statistics
                stats, created = AidLedgerStats.objects.get_or_create(
                    defaults={'total_donations': 0, 'total_distributions': 0}
                )
                stats.total_donations += Decimal(amount)
                stats.save()
            
            messages.success(request, f'Successfully donated {amount} AID to {ngo.name}!')
            return redirect('user_dashboard')
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    ngos = NGO.objects.all()
    return render(request, 'make_donation.html', {'ngos': ngos})


@login_required
def make_distribution_view(request):
    """View for NGOs to make distributions"""
    if not hasattr(request.user, 'customuser') or request.user.customuser.user_type != 'ngo':
        messages.error(request, 'Only NGOs can make distributions.')
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        amount = request.POST.get('amount')
        
        try:
            ngo = NGO.objects.get(user=request.user)
            recipient = Recipient.objects.get(id=recipient_id)
            
            # Create distribution directly
            with transaction.atomic():
                # Log to Hedera HCS
                txn_hash = hedera_service.log_distribution_to_hcs(
                    ngo.name, recipient.name, float(amount)
                )
                
                # Create distribution record
                distribution = Distribution.objects.create(
                    ngo=ngo,
                    recipient=recipient,
                    amount=amount,
                    txn_hash=txn_hash,
                    status='confirmed'
                )
                
                # Update statistics
                stats, created = AidLedgerStats.objects.get_or_create(
                    defaults={'total_donations': 0, 'total_distributions': 0}
                )
                stats.total_distributions += Decimal(amount)
                stats.save()
            
            messages.success(request, f'Successfully distributed {amount} AID to {recipient.name}!')
            return redirect('user_dashboard')
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    recipients = Recipient.objects.all()
    return render(request, 'make_distribution.html', {'recipients': recipients})


def dashboard_view(request):
    """Main public dashboard view"""
    context = {
        'donations': Donation.objects.all().order_by('-timestamp')[:10],
        'distributions': Distribution.objects.all().order_by('-timestamp')[:10],
        'stats': AidLedgerStats.objects.first()
    }
    return render(request, 'dashboard.html', context)


@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    try:
        custom_user = CustomUser.objects.get(user=user)
        
        if custom_user.user_type == 'donor':
            profile = Donor.objects.get(user=user)
        elif custom_user.user_type == 'ngo':
            profile = NGO.objects.get(user=user)
        else:
            profile = None
            
        context = {
            'user': user,
            'custom_user': custom_user,
            'profile': profile
        }
        return render(request, 'profile.html', context)
        
    except (CustomUser.DoesNotExist, Donor.DoesNotExist, NGO.DoesNotExist):
        messages.error(request, 'Profile not found.')
        return redirect('user_dashboard')