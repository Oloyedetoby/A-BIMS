from django.db import models

# NEW: We are making a dedicated model for RouteAxis
class RouteAxis(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# NEW: We are making a dedicated model for Author
class Author(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Publisher(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.PROTECT)
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT)
    # ADD THIS NEW LINE FOR THE MASTER PRICE
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity_in_stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    

class Customer(models.Model):
    school_name = models.CharField(max_length=255)
    # UPDATED: This now links to the RouteAxis model
    route_axis = models.ForeignKey(RouteAxis, on_delete=models.PROTECT)
    address = models.TextField()
    contact_person = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, unique=True)
    # NEW: The referral field you requested
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referred_customers'
    )

    def __str__(self):
        return f"{self.school_name} ({self.route_axis})"

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
    
    

class CreditNote(models.Model):
    # Links to the customer and the original invoice being credited
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    original_invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    reason = models.CharField(max_length=255, blank=True, help_text="e.g., Unsold book returns")

    def __str__(self):
        return f"Credit Note #{self.id} for Invoice #{self.original_invoice.id}"

class CreditNoteItem(models.Model):
    credit_note = models.ForeignKey(CreditNote, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    # The price at which the book was returned, usually the original sale price
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.book.title} returned"