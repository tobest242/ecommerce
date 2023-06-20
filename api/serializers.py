from rest_framework import serializers
from storeapp.models import Product, Category, Review, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "get_absolute_url",
            "description",
            "price",
            "get_image",
            "get_thumbnail"
        )

        

class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)
    
    class Meta:
        model = Category
        fields = [ 'name', 'slug', 'get_absolute_url', 'products']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields =['id', 'date_created', 'name', 'description']
    
    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)




class MyOrderItemSerializer(serializers.ModelSerializer):    
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = (
            "price",
            "product",
            "quantity",
            "delivery_status",
        )


class MyOrderSerializer(serializers.ModelSerializer):
    items = MyOrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "first_name",
            "email",
            "phone",
            "items",
            "paid_amount"
        )

class OrderItemSerializer(serializers.ModelSerializer):    
    class Meta:
        model = OrderItem
        fields = (
            "price",
            "product",
            "quantity",
            "delivery_status",
        )

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "first_name",
            "email",
            "phone",
            "items",
            "tx_ref",

        )
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
        return order