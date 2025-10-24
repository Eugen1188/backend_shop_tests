from .serializers import ProfileSerializer
from .models import UserProfile
from rest_framework import generics
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from django.contrib.auth import logout
from .serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
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
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    OrderSerializer,
    ShippingAddressSerializer,
    OrderItemSerializer,
)

# ---------------------------
# Product & Category Views
# ---------------------------


class ProductListViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "name"]


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
        order = Order.objects.filter(user=request.user, status="Pending").first()
    else:
        session_id = request.session.get("cart_session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["cart_session_id"] = session_id
        order = Order.objects.filter(session_id=session_id, status="Pending").first()

    if not order:
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=(
                None
                if request.user.is_authenticated
                else request.session["cart_session_id"]
            ),
            status="Pending",
        )
    return order


# ---------------------------
# API Endpoints für Angular
# ---------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
def get_or_create_order_view(request):
    order = get_or_create_order(request)
    return Response({"id": order.id, "status": order.status})


@api_view(["POST"])
@permission_classes([AllowAny])
def add_to_order_view(request):
    order = get_or_create_order(request)

    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))
    color = request.data.get("color")
    size = request.data.get("size")

    if not product_id:
        return Response(
            {"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )

    order_item, created = OrderItem.objects.get_or_create(
        order=order, product=product, color=color, size=size
    )

    if not created:
        order_item.quantity += quantity
    else:
        order_item.quantity = quantity

    order_item.save()

    serializer = OrderItemSerializer(order_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def order_items_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    items = OrderItem.objects.filter(order=order)
    serializer = OrderItemSerializer(items, many=True)
    return Response(serializer.data)


@api_view(["PATCH", "DELETE"])
@permission_classes([AllowAny])
def order_item_detail_view(request, item_id):
    """Endpoint für einzelne OrderItems, PATCH für Menge erhöhen, DELETE für entfernen"""
    try:
        item = OrderItem.objects.get(id=item_id)
    except OrderItem.DoesNotExist:
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "PATCH":
        quantity = int(request.data.get("quantity", item.quantity))
        item.quantity = quantity
        item.save()
        serializer = OrderItemSerializer(item)
        return Response(serializer.data)

    if request.method == "DELETE":
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([AllowAny])  # 👈 allows anonymous access
def register_user(request):
    if request.method != "POST":
        return Response(
            {"success": False, "message": "Invalid request method."}, status=405
        )

    email = request.data.get("email")
    password = request.data.get("password")
    name = request.data.get("name")
    lastname = request.data.get("lastname")
    telefonumber = request.data.get("telefonumber")
    address = request.data.get("address")
    city = request.data.get("city")
    zip_code = request.data.get("zip_code")
    birthday = request.data.get("birthday")

    # Check if user already exists
    if User.objects.filter(email=email).exists():
        return Response(
            {"success": False, "message": "User with this email already exists."},
            status=400,
        )

    # Create user
    user = User.objects.create_user(
        username=name + lastname,
        email=email,
        password=password,
        first_name=name,
        last_name=lastname,
    )

    # Generate a verification token
    token = get_random_string(32)

    if not hasattr(user, "userprofile"):
        UserProfile.objects.create(
            user=user,
            telefonumber=telefonumber,
            address=address,
            birthday=birthday,
            city=city,
            zip_code=zip_code,
            verification_token=token,
            is_verified=False,
        )
    else:
        profile = user.userprofile
        if not profile.telefonumber:
            profile.telefonumber = telefonumber
        if not profile.address:
            profile.address = address
        if not profile.birthday:
            profile.birthday = birthday
        if not profile.city:
            profile.city = city
        if not profile.zip_code:
            profile.zip_code = zip_code
        profile.verification_token = token
        profile.is_verified = False
    profile.save()

    # Send verification email
    verification_link = (
        f"http://127.0.0.1:8000/api/verify-email/?token={token}&email={email}"
    )

    send_mail(
        subject="Verify your email",
        message=f"Click the link to verify your email: {verification_link}",
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({"success": True, "message": "Registration successful!"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_endpoint(request):
    return Response(
        {"message": f"Hello {request.user.username}, you are authenticated!"}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    user_profile = getattr(user, "userprofile", None)

    # Construct response data
    response_data = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "telefonnumber": user_profile.telefonumber if user_profile else "",
        "address": user_profile.address if user_profile else "",
        "city": user_profile.city if user_profile else "",
        "zip_code": user_profile.zip_code if user_profile else "",
        "birthday": user_profile.birthday if user_profile else "",
    }

    return Response(response_data)


@api_view(["GET"])
@permission_classes([AllowAny])  # 👈 allows anonymous access
def verify_email(request):
    token = request.query_params.get("token")
    email = request.query_params.get("email")

    if not token or not email:
        return Response({"error": "Invalid verification link"}, status=400)

    try:
        user = User.objects.get(email=email)
        profile = user.userprofile
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if profile.verification_token == token:
        profile.is_verified = True
        profile.verification_token = ""
        profile.save()
        # Redirect to Angular success page
        return HttpResponseRedirect("http://localhost:4200/verified-email")
    else:
        return Response({"error": "Invalid token"}, status=400)


@api_view(["POST"])
def request_password_reset(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required"}, status=400)

    try:
        user = User.objects.get(email=email)
        profile = user.userprofile
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    token = get_random_string(length=32)
    profile.password_reset_token = token
    profile.save()

    reset_link = f"http://localhost:4200/reset-password?token={token}&email={email}"

    # Render HTML template
    html_content = render_to_string(
        "emails/password_reset.html",
        {
            "username": user.username,
            "reset_link": reset_link,
        },
    )

    # Fallback plain-text
    text_content = f"Hallo {user.username}, nutze diesen Link: {reset_link}"

    msg = EmailMultiAlternatives(
        subject="Passwort zurücksetzen",
        body=text_content,
        from_email="john455454@gmail.com",
        to=[email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)

    return Response({"message": "Password reset email sent!"})


@api_view(["POST"])
def reset_password(request):
    email = request.data.get("email")
    token = request.data.get("token")
    new_password = request.data.get("password")

    if not all([email, token, new_password]):
        return Response({"error": "Missing fields"}, status=400)

    try:
        user = User.objects.get(email=email)
        profile = user.userprofile
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if profile.password_reset_token != token:
        return Response({"error": "Invalid token"}, status=400)

    user.set_password(new_password)
    user.save()

    profile.password_reset_token = ""  # clear the token
    profile.save()

    return Response({"message": "Password reset successfully!"})


# views.py
class MyTokenObtainPairView(TokenObtainPairView):

    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        print("Custom login endpoint called!")  # <-- debug message
        return super().post(request, *args, **kwargs)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def accountdelete(request):
    user = request.user
    user.delete()
    return Response({"detail": "Account deleted"}, status=status.HTTP_204_NO_CONTENT)


# views.py


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)
