from django.db.models.functions import Coalesce
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, F, Value, DecimalField, Prefetch, OuterRef, Subquery
from decimal import Decimal 
from .models import (
    Customer, Book, Publisher, Invoice, InvoiceItem,
    Payment, Author, RouteAxis, CreditNote
)
from .serializers import (
    CustomerSerializer, BookSerializer, PublisherSerializer, InvoiceSerializer,
    InvoiceWriteSerializer, DebtorInvoiceSerializer, RouteAxisSerializer, AuthorSerializer,
    CustomerDetailSerializer, CustomerWriteSerializer, BookDetailSerializer, BookWriteSerializer, CreditNoteWriteSerializer
)


# --- Primary Model ViewSets ---

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.prefetch_related(
        Prefetch('invoice_set', queryset=Invoice.objects.annotate(
            total_amount=Coalesce(Sum(F('items__quantity') * F('items__unit_price')), Value(0), output_field=DecimalField()),
            amount_paid=Coalesce(Sum('payment__amount'), Value(0), output_field=DecimalField()),
            credit_applied=Coalesce(Sum(F('creditnote__items__quantity')*F('creditnote__items__unit_price')), Value(0), output_field=DecimalField())
        ).annotate(
            balance_due=F('total_amount') - F('amount_paid') - F('credit_applied')
        )),
        'referred_customers'
    ).select_related('route_axis', 'referred_by').all()
    
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['author', 'publisher']
    search_fields = ['title']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return BookWriteSerializer
        return BookSerializer


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    ordering = ['name']


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    ordering = ['name']


class RouteAxisViewSet(viewsets.ModelViewSet):
    queryset = RouteAxis.objects.all()
    serializer_class = RouteAxisSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    ordering = ['name']

class CreditNoteViewSet(viewsets.ModelViewSet):
    queryset = CreditNote.objects.all()
    serializer_class = CreditNoteWriteSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    Final, stable version of the InvoiceViewSet.
    Calculations are now handled reliably by the serializer.
    """
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'customer']
    search_fields = ['id', 'customer__school_name', 'items__book__title']

    def get_queryset(self):
        # We go back to a simple, clean queryset.
        # This prevents all the annotation/grouping bugs.
        return Invoice.objects.select_related('customer').prefetch_related(
            'items__book', 'payment_set', 'creditnote_set__items'
        ).order_by('-invoice_date')

    # THE list() and retrieve() methods are REMOVED. We go back to the default behavior.

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InvoiceWriteSerializer
        return self.serializer_class


    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        invoice = self.get_object()
        
        # --- START: New Validation Logic ---
        amount_str = request.data.get('amount')
        notes = request.data.get('notes', '')

        if invoice.status == 'PAID':
            return Response({'error': 'This invoice has already been fully paid.'}, status=status.HTTP_400_BAD_REQUEST)

        if not amount_str:
            return Response({'error': 'Amount is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Payment amount must be positive.")
        except (ValueError, TypeError):
            return Response({'error': 'A valid, positive number is required for the amount.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate current balance before this new payment
        total_items = sum(i.quantity * (i.unit_price or 0) for i in invoice.items.all())
        total_paid_before = sum(p.amount for p in invoice.payment_set.all())
        total_credit = sum(ci.quantity * ci.unit_price for cn in invoice.creditnote_set.all() for ci in cn.items.all())
        balance_due_before = total_items - total_paid_before - total_credit

        if amount > balance_due_before:
            # As you suggested, we can handle overpayment later as store credit.
            # For now, we will prevent it to keep the logic simple and safe.
            return Response(
                {'error': f'Payment amount (₦{amount:.2f}) exceeds the balance due (₦{balance_due_before:.2f}).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # --- END: New Validation Logic ---

        # If all validation passes, create the payment
        Payment.objects.create(invoice=invoice, amount=amount, notes=notes)
        
        # Recalculate invoice status with the new payment included
        total_paid_after = total_paid_before + Decimal(amount)

        # Use a small tolerance for floating point comparisons
        if total_paid_after >= (Decimal(total_items) - Decimal(total_credit)):
            invoice.status = 'PAID'
        else:
            invoice.status = 'PARTIALLY_PAID'
        invoice.save()
        
        updated_invoice = self.get_queryset().get(pk=invoice.pk)
        serializer = self.get_serializer(updated_invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


@api_view(['GET'])
def debtors_list(request):
    credit_total_subquery = CreditNote.objects.filter(original_invoice=OuterRef('pk')).annotate(
        total=Coalesce(Sum(F('items__quantity') * F('items__unit_price')), Value(0), output_field=DecimalField())
    ).values('total')

    debtors = Invoice.objects.filter(
        Q(status='UNPAID') | Q(status='PARTIALLY_PAID')
    ).annotate(
        total_amount=Coalesce(Sum(F('items__quantity') * F('items__unit_price')), Value(0), output_field=DecimalField()),
        amount_paid=Coalesce(Sum('payment__amount'), Value(0), output_field=DecimalField()),
        credit_applied=Coalesce(Subquery(credit_total_subquery, output_field=DecimalField()), Value(0), output_field=DecimalField())
    ).annotate(
        balance_due=F('total_amount') - F('amount_paid') - F('credit_applied')
    ).select_related('customer').order_by('due_date')
    
    serializer = DebtorInvoiceSerializer(debtors, many=True)
    return Response(serializer.data)