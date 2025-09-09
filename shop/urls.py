from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductListViewset, CategoryListAPIView, get_or_create_order_view

router = DefaultRouter()
router.register(r'products', ProductListViewset, basename='product')


urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('orders/get_or_create/', get_or_create_order_view, name='get-or-create-order'),
    path('', include(router.urls)),
]
