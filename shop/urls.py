from django.urls import path
from .views import CategoryListAPIView, ProductListViewset

urlpatterns = [
    path('products/', ProductListViewset.as_view(), name='product-list'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
]