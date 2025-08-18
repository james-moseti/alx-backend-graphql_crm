# crm/models.py
from django.db import models
from django.core.validators import EmailValidator
import re
from django.core.exceptions import ValidationError


def validate_phone(value):
    """Validate phone number format"""
    if value:
        # Allow formats like +1234567890 or 123-456-7890
        phone_pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4}|\d{10,15})$'
        if not re.match(phone_pattern, value):
            raise ValidationError('Phone number must be in format +1234567890 or 123-456-7890')


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True, null=True, validators=[validate_phone])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.price <= 0:
            raise ValidationError('Price must be positive')

    class Meta:
        ordering = ['name']


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total(self):
        """Calculate total amount from associated products"""
        return sum(product.price for product in self.products.all())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.products.exists():
            self.total_amount = self.calculate_total()
            super().save(update_fields=['total_amount'])

    def __str__(self):
        return f"Order {self.id} - {self.customer.name}"

    class Meta:
        ordering = ['-order_date']