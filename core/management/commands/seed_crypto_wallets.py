# core/management/commands/seed_crypto_wallets.py
from django.core.management.base import BaseCommand
from core.models import CryptoWallet

class Command(BaseCommand):
    help = 'Seed initial crypto wallets'

    def handle(self, *args, **options):
        wallets_data = [
            {
                'currency': 'BTC',
                'wallet_address': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
                'is_active': True
            },
            {
                'currency': 'ETH',
                'wallet_address': '0x71C7656EC7ab88b098defB751B7401B5f6d8976F',
                'is_active': True
            },
            {
                'currency': 'USDT',
                'wallet_address': '0x71C7656EC7ab88b098defB751B7401B5f6d8976F',  # Same as ETH for ERC-20
                'is_active': True
            },
        ]
        
        for wallet_data in wallets_data:
            wallet, created = CryptoWallet.objects.get_or_create(
                currency=wallet_data['currency'],
                defaults=wallet_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created {wallet.get_currency_display()} wallet'))
            else:
                self.stdout.write(self.style.WARNING(f'🔄 Updated {wallet.get_currency_display()} wallet'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Crypto wallets seeded successfully!'))