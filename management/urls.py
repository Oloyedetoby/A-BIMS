from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, BookViewSet, PublisherViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'books', BookViewSet)
router.register(r'publishers', PublisherViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]