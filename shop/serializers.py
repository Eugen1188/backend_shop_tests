from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'products']

    def get_products(self, obj):
        products = obj.products.all()
        return ProductSerializer(products, many=True).data


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'category_id']

    def get_category(self, obj):
        return {"id": obj.category.id, "name": obj.category.name} if obj.category else None


