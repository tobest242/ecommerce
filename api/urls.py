from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

urlpatterns = [
    path('products/', views.ProductsList.as_view()),
    path('products/search/', views.search),
    path('checkout/', views.checkout),
    path('orders/', views.OrdersList.as_view()),
    path('confirm-payment/', views.payment_response),
    path('products/<slug:category_slug>/<slug:product_slug>/', views.ProductDetail.as_view()),
    path('products/<slug:category_slug>/', views.CategoryDetail.as_view()),
    path('category/', views.CategoryList.as_view(),)
]