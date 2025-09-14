from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from shop.models import UserProfile
from django.contrib.auth.models import User
import uuid
from rest_framework import generics, filters, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Order, ShippingAddress, OrderItem
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, ShippingAddressSerializer, OrderItemSerializer

# ---------------------------
# Product & Category Views
# ---------------------------


class ProductListViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
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
        order = Order.objects.filter(
            user=request.user, status='Pending').first()
    else:
        session_id = request.session.get('cart_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['cart_session_id'] = session_id
        order = Order.objects.filter(
            session_id=session_id, status='Pending').first()

    if not order:
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=None if request.user.is_authenticated else request.session[
                'cart_session_id'],
            status='Pending'
        )
    return order

# ---------------------------
# API Endpoints für Angular
# ---------------------------


@api_view(['GET'])
@permission_classes([AllowAny])
def get_or_create_order_view(request):
    order = get_or_create_order(request)
    return Response({
        'id': order.id,
        'status': order.status
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def add_to_order_view(request):
    order = get_or_create_order(request)

    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))

    if not product_id:
        return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    order_item, created = OrderItem.objects.get_or_create(
        order=order, product=product)
    if not created:
        order_item.quantity += quantity
    else:
        order_item.quantity = quantity
    order_item.save()

    serializer = OrderItemSerializer(order_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def order_items_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    items = OrderItem.objects.filter(order=order)
    serializer = OrderItemSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['PATCH', 'DELETE'])
@permission_classes([AllowAny])
def order_item_detail_view(request, item_id):
    """Endpoint für einzelne OrderItems, PATCH für Menge erhöhen, DELETE für entfernen"""
    try:
        item = OrderItem.objects.get(id=item_id)
    except OrderItem.DoesNotExist:
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        quantity = int(request.data.get('quantity', item.quantity))
        item.quantity = quantity
        item.save()
        serializer = OrderItemSerializer(item)
        return Response(serializer.data)

    if request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def register_user(request):
    if request.method != 'POST':
        return Response({'success': False, 'message': 'Invalid request method.'}, status=405)

    email = request.data.get('email')
    password = request.data.get('password')
    name = request.data.get('name')
    lastname = request.data.get('lastname')
    telefonumber = request.data.get('telefonumber')
    address = request.data.get('address')
    birthday = request.data.get('birthday')

    # Check if user already exists
    if User.objects.filter(email=email).exists():
        return Response({'success': False, 'message': 'User with this email already exists.'}, status=400)

    # Create user
    user = User.objects.create_user(
        username=name + lastname,
        email=email,
        password=password,
        first_name=name,
        last_name=lastname
    )

    # Create profile if it doesn't exist, otherwise update it
    if not hasattr(user, 'userprofile'):
        UserProfile.objects.create(
            user=user,
            telefonumber=telefonumber,
            address=address,
            birthday=birthday
        )
    else:
        profile = user.userprofile
        if not profile.telefonumber:
            profile.telefonumber = telefonumber
        if not profile.address:
            profile.address = address
        if not profile.birthday:
            profile.birthday = birthday
        profile.save()

    return Response({'success': True, 'message': 'Registration successful!'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_endpoint(request):
    return Response({"message": "Hello, JWT works!"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    })
