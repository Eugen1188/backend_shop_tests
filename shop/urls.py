from django.urls import path
from .views import CategoryListAPIView, ProductListViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', ProductListViewset, basename='product')

urlpatterns = [
    # path('products/', ProductListViewset.as_view(), name='product-list'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    router.urls,
]