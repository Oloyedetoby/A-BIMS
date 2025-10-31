from django.contrib import admin
# Add your new models to this import line
from .models import Publisher, Book, Customer, Invoice, InvoiceItem, Payment

# Register all your models here
admin.site.register(Publisher)
admin.site.register(Book)
admin.site.register(Customer)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Payment)