from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductListViewset, CategoryListAPIView, get_or_create_order_view, add_to_order_view, order_items_view, order_item_detail_view
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import profile_view
from .views import verify_email
from .views import reset_password, request_password_reset
from .views import MyTokenObtainPairView


router = DefaultRouter()
router.register(r'products', ProductListViewset, basename='product')

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('orders/get_or_create/', get_or_create_order_view,
         name='get-or-create-order'),
    path('order-items/', add_to_order_view, name='add-to-order'),
    path('orders/<int:order_id>/items/', order_items_view, name='order-items'),
    path('order-items/<int:item_id>/',
         order_item_detail_view, name='order-item-detail'),
    path('register/', views.register_user, name='register_user'),
    path('protected/endpoint', views.protected_endpoint, name='protected-endpoint'),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('profile/', profile_view, name='profile'),
    path('verify-email/', verify_email, name='verify-email'),
    path('password-reset-request/', request_password_reset,
         name='request-password-reset'),
    path('password-reset/', reset_password, name='reset-password'),
    path('login-token/', MyTokenObtainPairView.as_view(),
         name='custom_token_obtain_pair'),
    path('', include(router.urls)),
]
