import random
from django.core.management.base import BaseCommand
from faker import Faker
from management.models import Author, Publisher, RouteAxis, Customer, Book, Invoice, InvoiceItem, Payment

class Command(BaseCommand):
    help = 'Seeds the database with a large amount of realistic test data.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old data...')
        # Clear out the old data to prevent duplicates
        Payment.objects.all().delete()
        InvoiceItem.objects.all().delete()
        Invoice.objects.all().delete()
        Book.objects.all().delete()
        Customer.objects.all().delete()
        Author.objects.all().delete()
        Publisher.objects.all().delete()
        RouteAxis.objects.all().delete()

        fake = Faker()

        self.stdout.write('Creating master data...')
        # Create master data
        axes = [RouteAxis.objects.create(name=name) for name in ['Island', 'Mainland', 'Lekki-Ajah', 'Ikorodu', 'Surulere']]
        authors = [Author.objects.create(name=fake.name()) for _ in range(50)]
        publishers = [Publisher.objects.create(name=f"{fake.company()} Press") for _ in range(20)]

        self.stdout.write('Creating 200 books...')
        # Create Books
        books = []
        for _ in range(200):
            book = Book.objects.create(
                title=fake.catch_phrase().title(),
                author=random.choice(authors),
                publisher=random.choice(publishers),
                price=random.uniform(1000, 5000),
                quantity_in_stock=random.randint(50, 200)
            )
            books.append(book)

        self.stdout.write('Creating 100 customers...')
        # Create Customers
        customers = []
        for _ in range(100):
            customer = Customer.objects.create(
                school_name=f"{fake.city()} International School",
                route_axis=random.choice(axes),
                address=fake.address(),
                contact_person=fake.name(),
                phone_number=fake.msisdn() # Generates Nigerian-style numbers
            )
            customers.append(customer)
        
        # Add some referrals
        for customer in random.sample(customers, 20):
            possible_referrers = [c for c in customers if c.id != customer.id]
            customer.referred_by = random.choice(possible_referrers)
            customer.save()

        self.stdout.write('Creating 500 invoices...')
        # Create Invoices and Payments
        for i in range(500):
            customer = random.choice(customers)
            invoice_status = random.choice(['UNPAID', 'PARTIALLY_PAID', 'PAID'])
            invoice = Invoice.objects.create(
                customer=customer,
                due_date=fake.date_between(start_date='-30d', end_date='+30d'),
                status=invoice_status
            )
            
            # Add items to the invoice
            total_amount = 0
            for _ in range(random.randint(1, 5)):
                book = random.choice(books)
                quantity = random.randint(1, 10)
                # Don't sell more than available stock
                if book.quantity_in_stock >= quantity:
                    item = InvoiceItem.objects.create(
                        invoice=invoice,
                        book=book,
                        quantity=quantity,
                        unit_price=book.price
                    )
                    book.quantity_in_stock -= quantity
                    book.save()
                    total_amount += item.quantity * item.unit_price
            
            # Add payments based on status
            if invoice_status == 'PAID':
                Payment.objects.create(invoice=invoice, amount=total_amount)
            elif invoice_status == 'PARTIALLY_PAID' and total_amount > 0:
                Payment.objects.create(invoice=invoice, amount=total_amount / 2)

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!'))