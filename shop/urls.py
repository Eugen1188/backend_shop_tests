from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductListViewset, CategoryListAPIView, get_or_create_order_view, add_to_order_view, order_items_view, order_item_detail_view

router = DefaultRouter()
router.register(r'products', ProductListViewset, basename='product')

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('orders/get_or_create/', get_or_create_order_view, name='get-or-create-order'),
    path('order-items/', add_to_order_view, name='add-to-order'),
    path('orders/<int:order_id>/items/', order_items_view, name='order-items'),
    path('order-items/<int:item_id>/', order_item_detail_view, name='order-item-detail'),
    path('api/register/', views.register_user, name='register_user'),
    path('', include(router.urls)),
]
