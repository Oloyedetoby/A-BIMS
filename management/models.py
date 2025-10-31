from django.db import models

# This class will become the "Publisher" table in the database
class Publisher(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

# This class will become the "Book" table
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    # This creates a link to the Publisher table. Each book belongs to one publisher.
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

# This class will become the "Customer" table (for the schools)
class Customer(models.Model):
    school_name = models.CharField(max_length=255)
    route_axis = models.CharField(max_length=100, help_text="e.g., North, Island, Mainland")
    address = models.TextField()
    contact_person = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.school_name} ({self.route_axis})"
    
    

# ADD THIS NEW CODE AT THE BOTTOM OF management/models.py

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('UNPAID', 'Unpaid'),
        ('PAID', 'Paid'),
        ('PARTIALLY_PAID', 'Partially Paid'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UNPAID')

    def __str__(self):
        return f"Invoice #{self.id} for {self.customer.school_name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # We use DecimalField for money to avoid rounding errors.
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.book.title}"

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    payment_date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payment of {self.amount} for Invoice #{self.invoice.id}"