from django.urls import include, path
from .views import CategoryListAPIView, ProductListViewset, OrderListCreateView, ShippingAddressListCreateView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', ProductListViewset, basename='product')

urlpatterns = [
    # path('products/', ProductListViewset.as_view(), name='product-list'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('orders/', OrderListCreateView.as_view(), name='order-list'),
    path('', include(router.urls)),
]