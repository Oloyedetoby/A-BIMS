from rest_framework import viewsets
from .models import Customer, Book, Publisher
from .serializers import CustomerSerializer, BookSerializer, PublisherSerializer

# This viewset automatically provides `list`, `create`, `retrieve`,
# `update`, and `destroy` actions.
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer