from django.contrib import admin
from .models import Product, Category, Order, ProductImage
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1 

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False  
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Order)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)