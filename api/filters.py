from django_filters.rest_framework import FilterSet
from storeapp.models import Product


class Productfilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'category': ['exact'],
            'price': ['gt', 'lt']
        }
