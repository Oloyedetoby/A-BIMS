from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Q, Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce
from rest_framework import viewsets, status, filters 
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import RouteAxisSerializer 
from .models import ( CreditNote, Customer, Book, Publisher, Invoice, InvoiceItem, Payment, Author, RouteAxis )
from .serializers import ( CustomerSerializer, BookSerializer, PublisherSerializer, InvoiceSerializer, InvoiceWriteSerializer, DebtorInvoiceSerializer )
from django.db.models import OuterRef, Subquery


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.select_related('route_axis', 'referred_by').all()
    serializer_class = CustomerSerializer
    
    # MODIFY this line to add the new backend
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    # ADD THIS LINE to specify filterable fields
    filterset_fields = ['route_axis']
    
    search_fields = ['school_name', 'contact_person', 'phone_number', 'address']

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('author', 'publisher').all()
    serializer_class = BookSerializer

class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'customer'] 
    
    def get_queryset(self):
        # Subquery to calculate the total value of credit notes for each invoice
        credit_total_subquery = CreditNote.objects.filter(
            original_invoice=OuterRef('pk')
        ).annotate(
            total=Sum(F('items__quantity') * F('items__unit_price'))
        ).values('total')

        return Invoice.objects.annotate(
            total_amount=Coalesce(Sum(F('items__quantity') * F('items__unit_price')), Value(0), output_field=DecimalField()),
            amount_paid=Coalesce(Sum('payment__amount'), Value(0), output_field=DecimalField()),
            # NEW: Add the total credit applied
            credit_applied=Coalesce(Subquery(credit_total_subquery, output_field=DecimalField()), Value(0), output_field=DecimalField())
        ).annotate(
            # NEW: The balance due calculation is now credit-aware
            balance_due=F('total_amount') - F('amount_paid') - F('credit_applied')
        ).select_related('customer').prefetch_related('items__book', 'payment_set').order_by('-invoice_date')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InvoiceWriteSerializer
        return self.serializer_class

    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        invoice = self.get_object()
        amount_str = request.data.get('amount')
        notes = request.data.get('notes', '')
        if not amount_str:
            return Response({'error': 'Amount is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount = float(amount_str)
            if amount <= 0: raise ValueError("Payment amount must be positive.")
        except (ValueError, TypeError):
            return Response({'error': 'A valid, positive number is required for the amount.'}, status=status.HTTP_400_BAD_REQUEST)
        Payment.objects.create(invoice=invoice, amount=amount, notes=notes)
        total_paid = invoice.payment_set.aggregate(total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField()))['total']
        total_amount = sum(item.quantity * (item.unit_price or 0) for item in invoice.items.all())
        if total_paid >= total_amount:
            invoice.status = 'PAID'
        else:
            invoice.status = 'PARTIALLY_PAID'
        invoice.save()
        updated_invoice = self.get_queryset().get(pk=invoice.pk)
        serializer = self.get_serializer(updated_invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def dashboard_stats(request):
    customer_count = Customer.objects.count()
    book_count = Book.objects.count()
    debtors_count = Invoice.objects.filter(Q(status='UNPAID') | Q(status='PARTIALLY_PAID')).count()
    stats = { 'customer_count': customer_count, 'book_count': book_count, 'debtors_count': debtors_count, }
    return Response(stats)


@api_view(['GET'])
def debtors_list(request):
    credit_total_subquery = CreditNote.objects.filter(original_invoice=OuterRef('pk')).annotate(
        total=Sum(F('items__quantity') * F('items__unit_price'))
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



class RouteAxisViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RouteAxis.objects.all()
    serializer_class = RouteAxisSerializer