# core/management/commands/seed_payment_plans.py
from django.core.management.base import BaseCommand
from core.models import PaymentPlan

class Command(BaseCommand):
    help = 'Seed payment plans data only'

    def handle(self, *args, **options):
        plans_data = [
            {
                'name': 'starter',
                'description': 'Basic investigation for smaller cases under $1,000. Perfect for straightforward crypto or payment scams.',
                'min_amount': 0,
                'max_amount': 1000,
                'deposit_percentage': 15,
                'fixed_deposit': None,
                'features': [
                    'Basic blockchain investigation',
                    'Wallet address tracing', 
                    'Transaction analysis',
                    'Email support (48h response)',
                    'Basic evidence review'
                ]
            },
            {
                'name': 'standard', 
                'description': 'Comprehensive recovery for medium-sized cases between $1,000 - $10,000. Includes dedicated agent support.',
                'min_amount': 1000,
                'max_amount': 10000,
                'deposit_percentage': 12,
                'fixed_deposit': None,
                'features': [
                    'Dedicated recovery agent',
                    'Advanced blockchain analysis',
                    'Multi-wallet tracing',
                    'Legal consultation included',
                    'Priority support (24h response)',
                    'Regular progress updates',
                    'Evidence documentation'
                ]
            },
            {
                'name': 'premium',
                'description': 'Full-scale professional recovery for major cases over $10,000. Includes legal action and expedited processing.',
                'min_amount': 10000,
                'max_amount': 1000000,
                'deposit_percentage': 10,
                'fixed_deposit': None,
                'features': [
                    'Premium recovery specialist',
                    'Full digital forensics',
                    'Cross-chain tracing',
                    'Legal action preparation',
                    '24/7 priority support',
                    'Expedited processing',
                    'Regular video call updates',
                    'Recovery guarantee (terms apply)',
                    'Multi-currency support'
                ]
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for plan_data in plans_data:
            plan, created = PaymentPlan.objects.update_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created {plan.get_name_display()}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Updated {plan.get_name_display()}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Successfully seeded payment plans! '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )