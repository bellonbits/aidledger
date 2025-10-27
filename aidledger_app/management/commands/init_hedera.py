from django.core.management.base import BaseCommand
from django.conf import settings
from aidledger_app.hedera_service import hedera_service


class Command(BaseCommand):
    help = 'Initialize Hedera services (HCS topic and AidCoin token)'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Initializing AidLedger Hedera Services...')
        )
        
        try:
            # Create HCS topic for transparency
            self.stdout.write('📝 Creating HCS topic for donation transparency...')
            topic_id = hedera_service.create_transparency_topic()
            self.stdout.write(
                self.style.SUCCESS(f'✅ HCS Topic created: {topic_id}')
            )
            
            # Create AidCoin token
            self.stdout.write('🪙 Creating AidCoin token...')
            token_id = hedera_service.create_aidcoin_token()
            self.stdout.write(
                self.style.SUCCESS(f'✅ AidCoin token created: {token_id}')
            )
            
            self.stdout.write(
                self.style.SUCCESS('🎉 Hedera services initialized successfully!')
            )
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Please update your .env file with the new IDs:\n'
                    f'TOPIC_ID={topic_id}\n'
                    f'TOKEN_ID={token_id}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to initialize Hedera services: {e}')
            )
            raise
