from django.contrib import admin
from .models import Product
from .models import Sale, SaleItem, Product
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(SaleItem)