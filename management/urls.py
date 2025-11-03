# THIS IS THE FULL, CORRECT urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet, BookViewSet, PublisherViewSet, dashboard_stats, 
    InvoiceViewSet, debtors_list, RouteAxisViewSet, AuthorViewSet
)
from .views import CreditNoteViewSet 


router = DefaultRouter()
router.register(r'credit-notes', CreditNoteViewSet, basename='creditnote')
router.register(r'customers', CustomerViewSet)
router.register(r'books', BookViewSet, basename='book')
router.register(r'publishers', PublisherViewSet)
router.register(r'route-axes', RouteAxisViewSet, basename='routeaxis')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
# THIS IS THE REGISTRATION THAT WAS MISSING
router.register(r'authors', AuthorViewSet, basename='author')

urlpatterns = [
    path('dashboard-stats/', dashboard_stats, name='dashboard-stats'),
    path('debtors/', debtors_list, name='debtors-list'),
    path('', include(router.urls)),
]