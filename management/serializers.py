from rest_framework import serializers
from django.db.models import Sum
from decimal import Decimal
from .models import (
    Customer, Book, Publisher, Invoice, InvoiceItem,
    Payment, Author, RouteAxis, CreditNote, CreditNoteItem
)

# --- Base "Read" Serializers (Define these first) ---

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'contact_person', 'phone_number']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']

class RouteAxisSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteAxis
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    publisher = serializers.StringRelatedField()
    author = serializers.StringRelatedField()
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'publisher', 'price', 'quantity_in_stock']

class CustomerSerializer(serializers.ModelSerializer):
    route_axis = serializers.StringRelatedField()
    referred_by = serializers.StringRelatedField()
    class Meta:
        model = Customer
        fields = ['id', 'school_name', 'route_axis', 'address', 'contact_person', 'phone_number', 'referred_by']

class InvoiceItemSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    book_id = serializers.IntegerField(source='book.id', read_only=True) 

    class Meta:
        model = InvoiceItem
        fields = ['id', 'book', 'book_id', 'quantity', 'unit_price'] 
        

# THIS CLASS MUST BE DEFINED BEFORE InvoiceSerializer
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_date', 'amount', 'notes']


# --- Complex "Read" Serializers ---

class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.school_name', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(source='payment_set', many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    credit_applied = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Invoice
        fields = [
            'id', 'customer_name', 'invoice_date', 'due_date', 'status', 'items', 'payments', 
            'total_amount', 'amount_paid', 'balance_due', 'credit_applied'
        ]

class BookSaleHistorySerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='invoice.customer.school_name', read_only=True)
    invoice_id = serializers.IntegerField(source='invoice.id', read_only=True)
    date = serializers.DateField(source='invoice.invoice_date', read_only=True)
    class Meta:
        model = InvoiceItem
        fields = ['invoice_id', 'date', 'customer_name', 'quantity', 'unit_price']

class BookDetailSerializer(serializers.ModelSerializer):
    # THIS IS THE KEY CHANGE
    author = AuthorSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    
    sale_history = BookSaleHistorySerializer(many=True, read_only=True, source='invoiceitem_set')
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'publisher', 'price', 'quantity_in_stock', 'sale_history']

class ReferredCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'school_name', 'route_axis']

class NestedInvoiceSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_date', 'status', 'total_amount', 'amount_paid', 'balance_due']

class CustomerDetailSerializer(serializers.ModelSerializer):
    route_axis = serializers.StringRelatedField()
    referred_by = ReferredCustomerSerializer(read_only=True)
    invoices = NestedInvoiceSerializer(many=True, read_only=True, source='invoice_set')
    referred_customers = ReferredCustomerSerializer(many=True, read_only=True)
    class Meta:
        model = Customer
        fields = [
            'id', 'school_name', 'route_axis', 'address', 'contact_person', 
            'phone_number', 'referred_by', 'invoices', 'referred_customers'
        ]


# --- "Write" Serializers for Creating/Updating Data ---

class CustomerWriteSerializer(serializers.ModelSerializer):
    route_axis_id = serializers.IntegerField()
    referred_by_id = serializers.IntegerField(allow_null=True, required=False)
    class Meta:
        model = Customer
        fields = ['school_name', 'contact_person', 'phone_number', 'address', 'route_axis_id', 'referred_by_id']
    def create(self, validated_data):
        route_axis_id = validated_data.pop('route_axis_id'); axis = RouteAxis.objects.get(id=route_axis_id); referred_by_id = validated_data.pop('referred_by_id', None); referred_by = None
        if referred_by_id: referred_by = Customer.objects.get(id=referred_by_id)
        customer = Customer.objects.create(route_axis=axis, referred_by=referred_by, **validated_data); return customer
    def update(self, instance, validated_data):
        instance.school_name = validated_data.get('school_name', instance.school_name); instance.contact_person = validated_data.get('contact_person', instance.contact_person); instance.phone_number = validated_data.get('phone_number', instance.phone_number); instance.address = validated_data.get('address', instance.address)
        if 'route_axis_id' in validated_data: axis = RouteAxis.objects.get(id=validated_data['route_axis_id']); instance.route_axis = axis
        if 'referred_by_id' in validated_data:
            referred_by_id = validated_data['referred_by_id']
            if referred_by_id: referred_by = Customer.objects.get(id=referred_by_id); instance.referred_by = referred_by
            else: instance.referred_by = None
        instance.save(); return instance

class BookWriteSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField()
    publisher_id = serializers.IntegerField()
    class Meta:
        model = Book
        fields = ['title', 'price', 'quantity_in_stock', 'author_id', 'publisher_id']
    def create(self, validated_data):
        author_id = validated_data.pop('author_id'); publisher_id = validated_data.pop('publisher_id'); author = Author.objects.get(id=author_id); publisher = Publisher.objects.get(id=publisher_id)
        book = Book.objects.create(author=author, publisher=publisher, **validated_data); return book
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title); instance.price = validated_data.get('price', instance.price); instance.quantity_in_stock = validated_data.get('quantity_in_stock', instance.quantity_in_stock)
        if 'author_id' in validated_data: author = Author.objects.get(id=validated_data['author_id']); instance.author = author
        if 'publisher_id' in validated_data: publisher = Publisher.objects.get(id=validated_data['publisher_id']); instance.publisher = publisher
        instance.save(); return instance

class InvoiceItemWriteSerializer(serializers.ModelSerializer):
    book_id = serializers.IntegerField()
    class Meta:
        model = InvoiceItem
        fields = ['book_id', 'quantity']

class InvoiceWriteSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField()
    items = InvoiceItemWriteSerializer(many=True)
    class Meta:
        model = Invoice
        fields = ['customer_id', 'due_date', 'status', 'items']
    def create(self, validated_data):
        items_data = validated_data.pop('items'); invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            try:
                book = Book.objects.get(id=item_data['book_id'])
                InvoiceItem.objects.create(invoice=invoice, book=book, quantity=item_data['quantity'], unit_price=book.price)
                book.quantity_in_stock -= item_data['quantity']; book.save()
            except Book.DoesNotExist: continue
        return invoice

class DebtorInvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.school_name', read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    credit_applied = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Invoice
        fields = ['id', 'customer_name', 'due_date', 'status', 'total_amount', 'amount_paid', 'balance_due', 'credit_applied']
        

class CreditNoteItemWriteSerializer(serializers.ModelSerializer):
    book_id = serializers.IntegerField()
    class Meta:
        model = CreditNoteItem
        fields = ['book_id', 'quantity', 'unit_price']

class CreditNoteWriteSerializer(serializers.ModelSerializer):
    items = CreditNoteItemWriteSerializer(many=True)
    class Meta:
        model = CreditNote
        fields = ['customer', 'original_invoice', 'reason', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        credit_note = CreditNote.objects.create(**validated_data)
        for item_data in items_data:
            # Create the credit note item
            CreditNoteItem.objects.create(credit_note=credit_note, **item_data)
            
            # And now, increase the stock for the returned book
            try:
                book = Book.objects.get(id=item_data['book_id'])
                book.quantity_in_stock += item_data['quantity']
                book.save()
            except Book.DoesNotExist:
                continue
        return credit_note