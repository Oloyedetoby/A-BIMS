from rest_framework import serializers
from .models import Customer, Book, Publisher

# This serializer will translate Publisher objects into JSON
class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'contact_person', 'phone_number']

# This serializer will translate Book objects into JSON
class BookSerializer(serializers.ModelSerializer):
    # We can customize how fields are displayed.
    # Here, we want to show the publisher's name, not just its ID.
    publisher = serializers.StringRelatedField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'publisher']

# This serializer will translate Customer objects into JSON
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'school_name', 'route_axis', 'address', 'contact_person', 'phone_number']