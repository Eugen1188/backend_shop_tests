from .models import UserProfile
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Category, Product, ProductImage, Order, OrderItem, ShippingAddress


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'color', 'color_code']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'images']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_id', 'quantity', 'color']


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'user', 'order', 'address', 'city', 'zip_code']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'shippingAddress',
                  'created_at', 'status', 'items']


# serializers.py


# serializers.py


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        identifier = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(username=identifier, password=password)
        if user is None:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(
                    username=user_obj.username, password=password)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "Kein Benutzer mit dieser Email"
                )
        if user is None:
            raise serializers.ValidationError(
                "Ungültiger Benutzername oder E-Mail oder Passwort."
            )

        # Check if email is verified
        if hasattr(user, 'userprofile'):
            if not user.userprofile.is_verified:
                raise serializers.ValidationError(
                    "E-Mail nicht verifiziert. Bitte bestätigen Sie Ihre E-Mail vor dem Login."
                )

        # ✅ Pass correct attrs to parent
        attrs['username'] = user.username
        attrs['password'] = password

        print("🔎 Final attrs before super:", attrs)

        return super().validate(attrs)


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = UserProfile
        fields = ['telefonumber', 'address', 'birthday',
                  'username', 'first_name', 'last_name', 'email', ]

    def update(self, instance, validated_data):
        print(validated_data)
        user_data = validated_data.pop('user', {})
        user = instance.user
        print(user_data)

        # Update related User fields
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
