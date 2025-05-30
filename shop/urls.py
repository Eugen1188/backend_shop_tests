from django.urls import path
from .views import CategoryListAPIView, ProductListCreateAPIView, ProductDetailAPIView

urlpatterns = [
    path('products/', ProductListCreateAPIView.as_view(), name='product-list'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
]