from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, F, Value, DecimalField, Prefetch, OuterRef, Subquery
from django.db.models.functions import Coalesce
from decimal import Decimal, ROUND_HALF_UP

from .models import (
    Customer, Book, Publisher, Invoice, InvoiceItem,
    Payment, Author, RouteAxis, CreditNote
)
from .serializers import (
    CustomerSerializer, BookSerializer, PublisherSerializer, InvoiceSerializer,
    InvoiceWriteSerializer, DebtorInvoiceSerializer, RouteAxisSerializer, AuthorSerializer,
    CustomerDetailSerializer, CustomerWriteSerializer, BookDetailSerializer, BookWriteSerializer,
    CreditNoteWriteSerializer, PublisherDetailSerializer, AuthorDetailSerializer, RouteAxisDetailSerializer
)
from rest_framework import generics
from rest_framework.filters import OrderingFilter

# --- Primary Model ViewSets ---

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.select_related(
        'route_axis', 'referred_by'
    ).prefetch_related(
        'invoice_set__items__book', 
        'invoice_set__payment_set', 
        'invoice_set__creditnote_set__items',
        'referred_customers'
    ).all()
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['route_axis']
    search_fields = ['school_name', 'contact_person', 'phone_number', 'address']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CustomerWriteSerializer
        if self.action == 'retrieve':
            return CustomerDetailSerializer
        return CustomerSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('author', 'publisher').prefetch_related(
        'invoiceitem_set__invoice__customer'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, OrderingFilter]
    filterset_fields = ['author', 'publisher']
    search_fields = ['title']
    
    ordering_fields = ['price', 'quantity_in_stock', 'title']
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return BookWriteSerializer
        return BookSerializer


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.prefetch_related('book_set__author')
    serializer_class = PublisherSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PublisherDetailSerializer
        return PublisherSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.prefetch_related('book_set__publisher')
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AuthorDetailSerializer
        return AuthorSerializer


class RouteAxisViewSet(viewsets.ModelViewSet):
    queryset = RouteAxis.objects.prefetch_related('customer_set')
    serializer_class = RouteAxisSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RouteAxisDetailSerializer
        return RouteAxisSerializer

class CreditNoteViewSet(viewsets.ModelViewSet):
    queryset = CreditNote.objects.all()
    serializer_class = CreditNoteWriteSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'customer']
    search_fields = ['id', 'customer__school_name', 'items__book__title']

    def get_queryset(self):
        return Invoice.objects.select_related('customer').prefetch_related(
            'items__book', 'payment_set', 'creditnote_set__items'
        ).order_by('-invoice_date')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InvoiceWriteSerializer
        return self.serializer_class

    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        invoice = self.get_object()
        amount_str = request.data.get('amount')
        notes = request.data.get('notes', '')

        if invoice.status == 'PAID':
            return Response({'error': 'This invoice has already been fully paid.'}, status=status.HTTP_400_BAD_REQUEST)
        if not amount_str:
            return Response({'error': 'Amount is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment_amount = Decimal(amount_str).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if payment_amount <= Decimal('0.00'):
                raise ValueError("Payment amount must be positive.")
        except (ValueError, TypeError):
            return Response({'error': 'A valid, positive number is required for the amount.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use serializer for precise balance check
        temp_serializer = InvoiceSerializer(invoice)
        balance_due_before = Decimal(temp_serializer.data.get('balance_due'))

        if payment_amount > (balance_due_before + Decimal('0.01')):
            return Response(
                {'error': f'Payment amount (₦{payment_amount:.2f}) exceeds the balance due (₦{balance_due_before:.2f}).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        Payment.objects.create(invoice=invoice, amount=payment_amount, notes=notes)
        
        invoice.refresh_from_db()
        
        # Re-serialize to get the new balance and status
        updated_serializer = InvoiceSerializer(invoice)
        new_balance_due = Decimal(updated_serializer.data.get('balance_due'))

        if new_balance_due <= Decimal('0.01'):
            invoice.status = 'PAID'
        else:
            invoice.status = 'PARTIALLY_PAID'
        invoice.save()
        
        final_serializer = InvoiceSerializer(invoice)
        return Response(final_serializer.data, status=status.HTTP_200_OK)


# --- Dashboard and Debtors API Views ---

@api_view(['GET'])
def dashboard_stats(request):
    customer_count = Customer.objects.count()
    book_count = Book.objects.count()
    debtors_count = Invoice.objects.filter(Q(status='UNPAID') | Q(status='PARTIALLY_PAID')).count()
    stats = {
        'customer_count': customer_count,
        'book_count': book_count,
        'debtors_count': debtors_count,
    }
    return Response(stats)


class DebtorsListView(generics.ListAPIView):
    """
    A dedicated, sortable list view for all debtors.
    Now with annotation to allow sorting by calculated fields.
    """
    serializer_class = DebtorInvoiceSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['due_date', 'balance_due', 'customer_name']
    ordering = ['due_date']
    
    pagination_class = None 
    
    def get_queryset(self):
        # THIS IS THE KEY FIX: We must annotate the calculated field
        # before the ordering filter can use it.
        credit_total_subquery = CreditNote.objects.filter(
            original_invoice=OuterRef('pk')
        ).values('original_invoice').annotate(
            total=Coalesce(Sum(F('items__quantity') * F('items__unit_price')), Value(0), output_field=DecimalField())
        ).values('total')

        return Invoice.objects.filter(
            Q(status='UNPAID') | Q(status='PARTIALLY_PAID')
        ).annotate(
            total_amount=Coalesce(Sum(F('items__quantity') * F('items__unit_price')), Value(0), output_field=DecimalField()),
            amount_paid=Coalesce(Sum('payment__amount'), Value(0), output_field=DecimalField()),
            credit_applied=Coalesce(Subquery(credit_total_subquery, output_field=DecimalField()), Value(0), output_field=DecimalField())
        ).annotate(
            balance_due=F('total_amount') - F('amount_paid') - F('credit_applied')
        ).select_related('customer').prefetch_related('items', 'payment_set')
        
        

@api_view(['GET'])
def business_insights(request):
    """
    An API view that calculates and returns key business intelligence metrics.
    """
    # --- Top 3 Highest Debtors ---
    # THIS IS THE CORRECTED and ROBUST QUERY
    highest_debtors_query = Customer.objects.annotate(
        total_invoiced=Coalesce(Sum(F('invoice__items__quantity') * F('invoice__items__unit_price')), Value(Decimal('0.00'))),
        total_paid=Coalesce(Sum('invoice__payment__amount'), Value(Decimal('0.00'))),
        total_credited=Coalesce(Sum(F('invoice__creditnote__items__quantity') * F('invoice__creditnote__items__unit_price')), Value(Decimal('0.00')))
    ).annotate(
        outstanding_balance=F('total_invoiced') - F('total_paid') - F('total_credited')
    ).filter(outstanding_balance__gt=0).order_by('-outstanding_balance')[:3]
    
    highest_debtors = [
        {'name': c.school_name, 'balance': c.outstanding_balance} for c in highest_debtors_query
    ]

    # --- Top 3 Best Customers (Lifetime Value) ---
    best_customers_query = Customer.objects.annotate(
        total_spent=Coalesce(Sum('invoice__payment__amount'), Value(Decimal('0.00')))
    ).order_by('-total_spent')[:3]

    best_customers = [
        {'name': c.school_name, 'total_spent': c.total_spent} for c in best_customers_query
    ]

    # --- Top 3 Best-Selling Books (by Revenue) ---
    best_selling_books_query = Book.objects.annotate(
        total_revenue=Coalesce(Sum(F('invoiceitem__quantity') * F('invoiceitem__unit_price')), Value(Decimal('0.00')))
    ).order_by('-total_revenue')[:3]

    best_selling_books = [
        {'title': b.title, 'revenue': b.total_revenue} for b in best_selling_books_query
    ]

    # --- Inventory Stats ---
    most_stocked_books = Book.objects.order_by('-quantity_in_stock')[:3].values('title', 'quantity_in_stock')
    lowest_stocked_books = Book.objects.order_by('quantity_in_stock')[:3].values('title', 'quantity_in_stock')

    # --- Compile the final response ---
    insights = {
        'highest_debtors': highest_debtors,
        'best_customers': best_customers,
        'best_selling_books': best_selling_books,
        'most_stocked_books': list(most_stocked_books),
        'lowest_stocked_books': list(lowest_stocked_books),
    }

    return Response(insights)