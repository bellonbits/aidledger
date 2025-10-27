from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Donor, NGO, Recipient, Donation, Distribution


class AidLedgerAPITestCase(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.donor = Donor.objects.create(
            name="Test Donor",
            email="test@example.com",
            wallet_id="0.0.1234567"
        )
        
        self.ngo = NGO.objects.create(
            name="Test NGO",
            region="Test Region",
            wallet_id="0.0.2234567",
            description="Test NGO description"
        )
        
        self.recipient = Recipient.objects.create(
            name="Test Recipient",
            location="Test Location",
            wallet_id="0.0.3234567"
        )
    
    def test_create_donor(self):
        """Test creating a donor via API"""
        data = {
            'name': 'New Donor',
            'email': 'newdonor@example.com',
            'wallet_id': '0.0.1234568'
        }
        response = self.client.post('/api/donors/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Donor.objects.count(), 2)
    
    def test_create_ngo(self):
        """Test creating an NGO via API"""
        data = {
            'name': 'New NGO',
            'region': 'New Region',
            'wallet_id': '0.0.2234568',
            'description': 'New NGO description'
        }
        response = self.client.post('/api/ngos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NGO.objects.count(), 2)
    
    def test_create_recipient(self):
        """Test creating a recipient via API"""
        data = {
            'name': 'New Recipient',
            'location': 'New Location',
            'wallet_id': '0.0.3234568'
        }
        response = self.client.post('/api/recipients/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipient.objects.count(), 2)
    
    def test_get_stats(self):
        """Test getting statistics"""
        response = self.client.get('/api/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_donations', response.data)
        self.assertIn('total_distributions', response.data)


class AidLedgerModelTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.donor = Donor.objects.create(
            name="Test Donor",
            email="test@example.com",
            wallet_id="0.0.1234567"
        )
        
        self.ngo = NGO.objects.create(
            name="Test NGO",
            region="Test Region",
            wallet_id="0.0.2234567"
        )
        
        self.recipient = Recipient.objects.create(
            name="Test Recipient",
            location="Test Location",
            wallet_id="0.0.3234567"
        )
    
    def test_donor_str(self):
        """Test donor string representation"""
        self.assertEqual(str(self.donor), "Test Donor (test@example.com)")
    
    def test_ngo_str(self):
        """Test NGO string representation"""
        self.assertEqual(str(self.ngo), "Test NGO (Test Region)")
    
    def test_recipient_str(self):
        """Test recipient string representation"""
        self.assertEqual(str(self.recipient), "Test Recipient (Test Location)")
    
    def test_donation_creation(self):
        """Test donation creation"""
        donation = Donation.objects.create(
            donor=self.donor,
            ngo=self.ngo,
            amount=1000.00,
            txn_hash="test_hash_123"
        )
        self.assertEqual(donation.amount, 1000.00)
        self.assertEqual(donation.status, 'pending')
    
    def test_distribution_creation(self):
        """Test distribution creation"""
        distribution = Distribution.objects.create(
            ngo=self.ngo,
            recipient=self.recipient,
            amount=500.00,
            txn_hash="test_hash_456"
        )
        self.assertEqual(distribution.amount, 500.00)
        self.assertEqual(distribution.status, 'pending')
