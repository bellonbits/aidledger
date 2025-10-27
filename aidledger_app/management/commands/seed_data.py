from django.core.management.base import BaseCommand
from aidledger_app.models import Donor, NGO, Recipient, AidLedgerStats


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🌱 Seeding AidLedger with sample data...')
        )
        
        # Create sample donors
        donors_data = [
            {'name': 'Alice Johnson', 'email': 'alice@example.com', 'wallet_id': '0.0.1234567'},
            {'name': 'Bob Smith', 'email': 'bob@example.com', 'wallet_id': '0.0.1234568'},
            {'name': 'Carol Davis', 'email': 'carol@example.com', 'wallet_id': '0.0.1234569'},
        ]
        
        for donor_data in donors_data:
            donor, created = Donor.objects.get_or_create(
                email=donor_data['email'],
                defaults=donor_data
            )
            if created:
                self.stdout.write(f'✅ Created donor: {donor.name}')
        
        # Create sample NGOs
        ngos_data = [
            {'name': 'Global Relief Foundation', 'region': 'Global', 'wallet_id': '0.0.2234567', 'description': 'International humanitarian organization'},
            {'name': 'Local Community Aid', 'region': 'North America', 'wallet_id': '0.0.2234568', 'description': 'Community-focused aid organization'},
            {'name': 'Emergency Response Team', 'region': 'Africa', 'wallet_id': '0.0.2234569', 'description': 'Rapid response humanitarian aid'},
        ]
        
        for ngo_data in ngos_data:
            ngo, created = NGO.objects.get_or_create(
                wallet_id=ngo_data['wallet_id'],
                defaults=ngo_data
            )
            if created:
                self.stdout.write(f'✅ Created NGO: {ngo.name}')
        
        # Create sample recipients
        recipients_data = [
            {'name': 'Maria Rodriguez', 'location': 'Mexico City, Mexico', 'wallet_id': '0.0.3234567'},
            {'name': 'Ahmed Hassan', 'location': 'Cairo, Egypt', 'wallet_id': '0.0.3234568'},
            {'name': 'Sarah Kim', 'location': 'Seoul, South Korea', 'wallet_id': '0.0.3234569'},
        ]
        
        for recipient_data in recipients_data:
            recipient, created = Recipient.objects.get_or_create(
                wallet_id=recipient_data['wallet_id'],
                defaults=recipient_data
            )
            if created:
                self.stdout.write(f'✅ Created recipient: {recipient.name}')
        
        # Initialize stats
        stats, created = AidLedgerStats.objects.get_or_create(
            defaults={
                'total_donations': 0,
                'total_distributions': 0,
                'total_donors': Donor.objects.count(),
                'total_ngos': NGO.objects.count(),
                'total_recipients': Recipient.objects.count()
            }
        )
        
        if created:
            self.stdout.write('✅ Initialized statistics')
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Sample data seeded successfully!')
        )
