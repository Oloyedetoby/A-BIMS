# THIS IS THE FULL, CORRECT urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet, BookViewSet, PublisherViewSet, dashboard_stats, 
    InvoiceViewSet, RouteAxisViewSet, AuthorViewSet
)
from .views import CreditNoteViewSet 
from .views import DebtorsListView 
from .views import business_insights 


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
    path('debtors/', DebtorsListView.as_view(), name='debtors-list'),
    path('insights/', business_insights, name='business-insights'),
    path('', include(router.urls)),
]

