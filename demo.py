#!/usr/bin/env python
"""
AidLedger Demo Script
Demonstrates how to use the AidLedger API to create donations and distributions
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000/api"

def create_donor():
    """Create a sample donor"""
    donor_data = {
        "name": "Demo Donor",
        "email": "demo@example.com",
        "wallet_id": "0.0.1234567"
    }
    
    response = requests.post(f"{BASE_URL}/donors/", json=donor_data)
    if response.status_code == 201:
        print("✅ Created donor:", response.json()['name'])
        return response.json()['id']
    else:
        print("❌ Failed to create donor:", response.text)
        return None

def create_ngo():
    """Create a sample NGO"""
    ngo_data = {
        "name": "Demo NGO",
        "region": "Global",
        "wallet_id": "0.0.2234567",
        "description": "Demo humanitarian organization"
    }
    
    response = requests.post(f"{BASE_URL}/ngos/", json=ngo_data)
    if response.status_code == 201:
        print("✅ Created NGO:", response.json()['name'])
        return response.json()['id']
    else:
        print("❌ Failed to create NGO:", response.text)
        return None

def create_recipient():
    """Create a sample recipient"""
    recipient_data = {
        "name": "Demo Recipient",
        "location": "Demo Location",
        "wallet_id": "0.0.3234567"
    }
    
    response = requests.post(f"{BASE_URL}/recipients/", json=recipient_data)
    if response.status_code == 201:
        print("✅ Created recipient:", response.json()['name'])
        return response.json()['id']
    else:
        print("❌ Failed to create recipient:", response.text)
        return None

def create_donation(donor_id, ngo_id, amount):
    """Create a donation"""
    donation_data = {
        "donor_id": donor_id,
        "ngo_id": ngo_id,
        "amount": str(amount)
    }
    
    response = requests.post(f"{BASE_URL}/donate/", json=donation_data)
    if response.status_code == 201:
        print(f"✅ Created donation: {amount} AID")
        return response.json()
    else:
        print("❌ Failed to create donation:", response.text)
        return None

def create_distribution(ngo_id, recipient_id, amount):
    """Create a distribution"""
    distribution_data = {
        "ngo_id": ngo_id,
        "recipient_id": recipient_id,
        "amount": str(amount)
    }
    
    response = requests.post(f"{BASE_URL}/distribute/", json=distribution_data)
    if response.status_code == 201:
        print(f"✅ Created distribution: {amount} AID")
        return response.json()
    else:
        print("❌ Failed to create distribution:", response.text)
        return None

def get_stats():
    """Get AidLedger statistics"""
    response = requests.get(f"{BASE_URL}/stats/")
    if response.status_code == 200:
        stats = response.json()
        print("\n📊 AidLedger Statistics:")
        print(f"   Total Donations: {stats['total_donations']} AID")
        print(f"   Total Distributions: {stats['total_distributions']} AID")
        print(f"   Total Donors: {stats['total_donors']}")
        print(f"   Total NGOs: {stats['total_ngos']}")
        print(f"   Total Recipients: {stats['total_recipients']}")
        return stats
    else:
        print("❌ Failed to get stats:", response.text)
        return None

def get_transactions():
    """Get all transactions"""
    response = requests.get(f"{BASE_URL}/transactions/")
    if response.status_code == 200:
        transactions = response.json()
        print("\n📋 Recent Transactions:")
        
        print("\n💰 Donations:")
        for donation in transactions['donations'][:3]:  # Show first 3
            print(f"   {donation['donor_name']} → {donation['ngo_name']}: {donation['amount']} AID")
        
        print("\n🎁 Distributions:")
        for distribution in transactions['distributions'][:3]:  # Show first 3
            print(f"   {distribution['ngo_name']} → {distribution['recipient_name']}: {distribution['amount']} AID")
        
        return transactions
    else:
        print("❌ Failed to get transactions:", response.text)
        return None

def main():
    """Main demo function"""
    print("🚀 AidLedger Demo Script")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/stats/", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to AidLedger server")
        print("   Make sure the server is running: python manage.py runserver")
        return
    
    print("✅ Connected to AidLedger server")
    
    # Create entities
    print("\n👥 Creating entities...")
    donor_id = create_donor()
    ngo_id = create_ngo()
    recipient_id = create_recipient()
    
    if not all([donor_id, ngo_id, recipient_id]):
        print("❌ Failed to create required entities")
        return
    
    # Create transactions
    print("\n💸 Creating transactions...")
    
    # Create donations
    donation1 = create_donation(donor_id, ngo_id, 1000.00)
    donation2 = create_donation(donor_id, ngo_id, 500.00)
    
    # Wait a moment for blockchain processing
    time.sleep(2)
    
    # Create distributions
    distribution1 = create_distribution(ngo_id, recipient_id, 750.00)
    distribution2 = create_distribution(ngo_id, recipient_id, 250.00)
    
    # Show results
    time.sleep(1)
    get_stats()
    get_transactions()
    
    print("\n🎉 Demo completed successfully!")
    print("   Visit http://localhost:8000 to see the dashboard")

if __name__ == "__main__":
    main()
