from django.contrib import admin
# Add 'include' to this import line
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add this line to include your API urls
    path('api/', include('management.urls')),
]