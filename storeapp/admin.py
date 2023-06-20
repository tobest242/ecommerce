from django.contrib import admin

from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'slug', 'price', 'in_stock', 'created', 'updated']
    list_filter = ['in_stock']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'product']

admin.site.register(Order)
admin.site.register(OrderItem)
