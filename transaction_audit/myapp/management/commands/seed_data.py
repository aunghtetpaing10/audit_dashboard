from django.core.management.base import BaseCommand
from myapp.models import Transaction
from django.contrib.auth.models import User
from decimal import Decimal
import random
from faker import Faker

class Command(BaseCommand):
    help = 'Seeds 10,000+ transactions'

    def handle(self, *args, **options):
        fake = Faker()
        users = User.objects.all()

        transactions = []
        for _ in range(10000):
            status = random.choice(['pending', 'completed', 'failed'])
            transactions.append(Transaction(
                amount=Decimal(random.uniform(10, 10000)),
                status=status,
                merchant=fake.company(),
                is_flagged=random.choice([True, False]),
                approved_by=random.choice(users) if users and status == 'completed' else None
            ))
        
        Transaction.objects.bulk_create(transactions)
        self.stdout.write(self.style.SUCCESS("Successfully seeded 10,000 transactions."))