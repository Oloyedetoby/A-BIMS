from django.contrib import admin
from .models import CreditNote, CreditNoteItem 
from .models import (
    Publisher, Book, Customer, Invoice, InvoiceItem,
    Payment, Author, RouteAxis
)

# These two lines are the most important part
admin.site.register(Author)
admin.site.register(RouteAxis)

# Register the rest of the models
admin.site.register(Publisher)
admin.site.register(Book)
admin.site.register(Customer)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Payment)
admin.site.register(CreditNote)
admin.site.register(CreditNoteItem)