from django.shortcuts import render, get_object_or_404
import requests
from django.http import JsonResponse
import uuid
from django.conf import settings
from django.http import Http404
from django.db.models import Q
from rest_framework.decorators import api_view
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer, OrderSerializer, MyOrderSerializer
from .filters import Productfilter
from storeapp.models import Product, Category, Review, Order, OrderItem
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.conf import settings
from rest_framework import status, authentication, permissions
from django.contrib.auth.models import User


class ProductsList(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

class ProductDetail(APIView):
    def get_object(self, category_slug, product_slug):
        try:
            return Product.objects.filter(category__slug=category_slug).get(slug=product_slug)
        except Product.DoesNotExist:
            raise Http404
    
    def get(self, request, category_slug, product_slug, format=None):
        product = self.get_object(category_slug, product_slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

class CategoryList(APIView):
    def get(self, request, format=None):
        category = Category.objects.all()
        serializer = CategorySerializer (category, many=True)
        return Response(serializer.data)  

class CategoryDetail(APIView):
    def get_object(self, category_slug):
        try:
            return Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            raise Http404
    
    def get(self, request, category_slug, format=None):
        category = self.get_object(category_slug)
        serializer = CategorySerializer(category)
        return Response(serializer.data)


@api_view(['POST', 'GET'])
def search(request):
    query = request.data.get('query', '')

    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    else:
        return Response({"products": []})

@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def checkout(request):
    try:
        data = request.data
        order = {
            'items': [],
            'total_amount': 0,
            'customer': {
                'email': data.get('email', ''),
                'phone': data.get('phone', ''),
            }
        }

        for item in data.get('items', []):
            product = Product.objects.get(id=item['product'])
            order['items'].append({
                'name': product.name,
                'price': str(product.price),
                'quantity': str(item['quantity']),
            })
            order['total_amount'] += product.price * item['quantity']

        tx_ref = uuid.uuid4().hex
        order['tx_ref'] = tx_ref

        payment_request = {
            'tx_ref': tx_ref,
            'amount': str(order['total_amount']),
            'currency': 'NGN',
            'redirect_url': 'http://localhost:8080/cart/success',
            'payment_options': 'card, mobilemoney, ussd',
            'customer': {
                'email': order['customer']['email'],
                'phonenumber': order['customer']['phone']
            },
            'customizations': {
                'title': 'MyStore',
                'description': 'Payment for items: ' + ', '.join([item['name'] for item in order['items']])
            }
        }

        response = requests.post('https://api.flutterwave.com/v3/payments', json=payment_request, headers={'Authorization': env(‘FLUTTER_KEY’)})

        if response.status_code == 200:
            response = response.json()
            if response['status'] == 'success':
                payment_url = response['data']['link']
                serializer = OrderSerializer(data=request.data)

                if serializer.is_valid():
                    serializer.save(user=request.user, paid_amount=order['total_amount'], tx_ref=tx_ref)  # save tx_ref in Order model
                    return JsonResponse({'link': payment_url})
        
        return JsonResponse({'error': 'Failed to create payment'})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'One or more products in the order do not exist'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': 'An error occurred while processing the request: ' + str(e)}, status=500)



from django.shortcuts import get_object_or_404
from django.http import JsonResponse

@api_view(['GET'])
def payment_response(request):
    status = request.GET.get('status', None)
    tx_ref = request.GET.get('tx_ref', None)
    
    if status == 'successful' and tx_ref:
        try:
            order = Order.objects.get(tx_ref=tx_ref)
            order.status = 'paid'
            order.save()
            return JsonResponse({'status': status, 'tx_ref': tx_ref})
        
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Invalid transaction reference (tx_ref)'}, status=400)
        
        except Exception as e:
            return JsonResponse({'error': 'An error occurred while processing the payment: ' + str(e)}, status=500)
    
    return JsonResponse({'error': 'Payment was not successful or transaction reference is missing'}, status=400)


class OrdersList(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        orders = Order.objects.filter(user=request.user)
        serializer = MyOrderSerializer(orders, many=True)
        return Response(serializer.data)

