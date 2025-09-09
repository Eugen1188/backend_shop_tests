import uuid
from django.shortcuts import render
from rest_framework import generics, filters, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Order, ShippingAddress
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, ShippingAddressSerializer

# ---------------------------
# Product & Category Views
# ---------------------------

class ProductListViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name']

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# ---------------------------
# Order & Shipping Views
# ---------------------------

class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class ShippingAddressListCreateView(generics.ListCreateAPIView):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer

# ---------------------------
# Hilfsfunktion für offene Bestellungen
# ---------------------------

def get_or_create_order(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, status='Pending').first()
    else:
        session_id = request.session.get('cart_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['cart_session_id'] = session_id
        order = Order.objects.filter(session_id=session_id, status='Pending').first()

    if not order:
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=None if request.user.is_authenticated else request.session['cart_session_id'],
            status='Pending'
        )
    return order

# ---------------------------
# API Endpoint für Angular
# ---------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def get_or_create_order_view(request):
    """
    Liefert die offene Bestellung zurück oder erstellt eine neue.
    Funktioniert für eingeloggte User und Gäste.
    """
    order = get_or_create_order(request)
    return Response({
        'id': order.id,
        'status': order.status
    })
