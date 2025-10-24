from django.core.management.base import BaseCommand
from app.revenue.models import Pendapatan
from app.users.models import User
import random

class Command(BaseCommand):
    help = 'Create test refund data by marking some completed transactions as refunded'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of transactions to mark as refunded (default: 5)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get some paid transactions
        paid_transactions = Pendapatan.objects.filter(
            payment_status='paid',
            booking__booking_status='completed'
        ).order_by('?')[:count]
        
        if not paid_transactions:
            self.stdout.write(self.style.ERROR('No paid completed transactions found to refund'))
            return
        
        refund_reasons = [
            'Customer requested cancellation due to bad weather',
            'Venue maintenance issues',
            'Customer illness - medical certificate provided',
            'Double booking error - admin refund',
            'Court not available at scheduled time',
            'Customer dissatisfied with court condition',
            'Payment error - duplicate charge',
            'Event cancelled by organizer',
        ]
        
        admin_users = User.objects.filter(role='admin')
        admin = admin_users.first() if admin_users.exists() else None
        admin_name = admin.username if admin else 'system'
        
        refunded_count = 0
        for txn in paid_transactions:
            reason = random.choice(refund_reasons)
            txn.payment_status = 'refunded'
            txn.notes = f"REFUND: {reason} | Processed by: {admin_name} | Original notes: {txn.notes or 'N/A'}"
            txn.save()
            refunded_count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'✓ Refunded: {txn.mitra.get_full_name()} - Rp {txn.net_amount:,.0f} - {reason[:50]}...'
            ))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Successfully created {refunded_count} test refunds!'
        ))
