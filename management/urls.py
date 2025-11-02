from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Import the new view
from .views import CustomerViewSet, BookViewSet, PublisherViewSet, RouteAxisViewSet, dashboard_stats, InvoiceViewSet, debtors_list

# The router setup stays the same
router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'books', BookViewSet)
router.register(r'publishers', PublisherViewSet)
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'route-axes', RouteAxisViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    # ADD THE NEW URL PATTERN HERE
    path('dashboard-stats/', dashboard_stats, name='dashboard-stats'),
    path('debtors/', debtors_list, name='debtors-list'),
    # This line for the router should be last
    path('', include(router.urls)),
]