from rest_framework import serializers
from django.db.models import Sum
from decimal import Decimal
from .models import ( Customer, Book, Publisher, Invoice, InvoiceItem, Payment, Author, RouteAxis )

class PublisherSerializer(serializers.ModelSerializer):
    class Meta: model = Publisher; fields = ['id', 'name', 'contact_person', 'phone_number']
class BookSerializer(serializers.ModelSerializer):
    publisher = serializers.StringRelatedField(); author = serializers.StringRelatedField()
    class Meta: model = Book; fields = ['id', 'title', 'author', 'publisher', 'price']
class CustomerSerializer(serializers.ModelSerializer):
    route_axis = serializers.StringRelatedField(); referred_by = serializers.StringRelatedField()
    class Meta: model = Customer; fields = ['id', 'school_name', 'route_axis', 'address', 'contact_person', 'phone_number', 'referred_by']
class InvoiceItemSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    class Meta: model = InvoiceItem; fields = ['id', 'book', 'quantity', 'unit_price']
    
    
# Find this block of code
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_date', 'amount', 'notes']


class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.school_name', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    # NEW: Add the payments field
    payments = PaymentSerializer(source='payment_set', many=True, read_only=True)
    credit_applied = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    # These fields come from the database annotations
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        # Add 'payments' to the fields list
        fields = [
            'id', 'customer_name', 'invoice_date', 'due_date', 'status', 'credit_applied',
            'items', 'payments', 'total_amount', 'amount_paid', 'balance_due'
        ]
    
    def to_representation(self, instance):
        # This safeguard method is still good, no changes needed here.
        data = super().to_representation(instance)
        data['total_amount'] = Decimal(getattr(instance, 'total_amount', 0) or 0)
        data['amount_paid'] = Decimal(getattr(instance, 'amount_paid', 0) or 0)
        data['balance_due'] = Decimal(getattr(instance, 'balance_due', 0) or 0)
        return data
    
    
class InvoiceItemWriteSerializer(serializers.ModelSerializer):
    book_id = serializers.IntegerField()
    class Meta: model = InvoiceItem; fields = ['book_id', 'quantity']
class InvoiceWriteSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(); items = InvoiceItemWriteSerializer(many=True)
    class Meta: model = Invoice; fields = ['customer_id', 'due_date', 'status', 'items']
    def create(self, validated_data):
        items_data = validated_data.pop('items'); invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            try:
                book = Book.objects.get(id=item_data['book_id'])
                InvoiceItem.objects.create(invoice=invoice, book=book, quantity=item_data['quantity'], unit_price=book.price)
            except Book.DoesNotExist: continue
        return invoice

class DebtorInvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.school_name', read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    credit_applied = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta: model = Invoice; fields = ['id', 'customer_name', 'due_date', 'status', 'total_amount','credit_applied', 'amount_paid', 'balance_due']
    


class RouteAxisSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteAxis
        fields = ['id', 'name']