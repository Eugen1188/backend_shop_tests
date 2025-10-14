import uuid
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='subcategories',
        null=True,
        blank=True
    )

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    color = models.CharField(max_length=50, blank=True)
    color_code = models.CharField(max_length=7, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.color or 'default'}"


class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.UUIDField(
        default=uuid.uuid4, editable=False, null=True, blank=True)
    shippingAddress = models.ForeignKey(
        'ShippingAddress',
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"Order #{self.id} - {self.user or 'Guest'}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=50, blank=True, null=True)  # <--- Farbe
    size = models.CharField(max_length=50, blank=True, null=True)   # optional Größe
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('order', 'product', 'color', 'size')


class ShippingAddress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, related_name='shipping_address',
                              on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    def __str__(self):
        order_info = f"Order ID: {self.order.id}" if self.order else "No specific order"
        user_info = f"User: {self.user.username}" if self.user else "Guest Address"
        return f"{user_info}, Address: {self.address}, {self.city}, {self.zip_code} ({order_info})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefonumber = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    birthday = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)  # <-- new
    verification_token = models.CharField(
        max_length=64, blank=True, null=True)  # <-- token
    password_reset_token = models.CharField(max_length=32, blank=True)  # new
    def __str__(self):
        return f'{self.user.username} Profile'
